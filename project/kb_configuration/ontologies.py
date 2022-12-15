from __future__ import annotations
import pandas as pd
from json import dumps
from SPARQLWrapper import SPARQLWrapper, JSON

def pad_string(s, pad='"'):
    return f"{pad}{s}{pad}"

# TODO: documentation
# TODO: rename to Predicate
class Predicate:
    """ Immutable N-ary compound predicate: functor_name(v1, v2, ..., vN) """
    def __init__(self, name, p_dict):
        self._name = name
        self._p_dict = p_dict

    def project(self, keys) -> Predicate:
        return Predicate(self._name,
                {k: v for k, v in self._p_dict.items() if k in keys})

    def hide(self, keys) -> Predicate:
        return Predicate(self._name,
                {k: v for k, v in self._p_dict.items() if k not in keys})

    def value(self, key, value) -> Predicate:
        if type(value) is str:
            value = dumps(value)

        new_dict = self._p_dict.copy()
        new_dict[key] = value
        return Predicate(self._name, new_dict)

    def get(self, key) -> Any:
        return self._p_dict[key]

    def get_dict(self) -> dict:
        return self._p_dict.copy()

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        arg_str = ','.join(map(str, self._p_dict.values()))
        return f"{self._name}({arg_str})."

class PredicateResult:
    def __init__(self, result, predicates):
        self.result = result
        self.ps = predicates

    def constant(self, key, value) -> PredicateResult:
        self.ps = [p.value(key, value) for p in self.ps]
        return self

    def closure(self, key, f) -> PredicateResult:
        assert callable(f)
        self.ps = [p.value(key, f()) for p in self.ps]
        return self

    def filter(self, f) -> PredicateResult:
        assert callable(f)
        self.ps = [p for p in self.ps if f(p.get_dict())]
        return self

    def unique(self, key) -> PredicateResult:
        """ Retain the last inserted duplicate predicate, filtered on a key """
        d = {p.get(key): p for p in self.ps}
        self.ps = list(d.values())
        return self

    def project(self, *keys) -> PredicateResult:
        self.ps = [p.project(keys) for p in self.ps]
        return self

    def hide(self, *keys) -> PredicateResult:
        self.ps = [p.hide(keys) for p in self.ps]
        return self

    def build(self) -> Result:
        self.result.add_predicates(self.ps)
        return self.result

# TODO: documentation
class Result:
    """ Simple data wrapper holding query results """
    def __init__(self, df):
        self.df = df
        self.predicates = []

    def add_predicates(self, predicates: [Predicate]) -> None:
        self.predicates.extend(predicates)

    def predicate(self, name, *args, **kwargs) -> PredicateResult: 
        """ Fluent builder of n-ary predicates """

        # TODO: move to function definition
        k_dict = kwargs.get('k_dict', {})
        v_dict = kwargs.get('v_dict', {})
        allow_empty = kwargs.get('allow_empty', False)
        default_type = kwargs.get('default_type', 'string')

        # concatenate keys and remove duplicates while preserving order
        args = list(dict.fromkeys(list(args) + list(k_dict.keys())))

        assert all(type(arg) in [str] for arg in args)
        new_predicates = []

        for _, row in self.df.iterrows():
            predicates = {}
            for arg in args:
                k = f"{arg}.value"
                v = None
                if k in self.df:
                    v = row[k]
                    v = v if pd.notna(v) else None

                    # apply optional computation to the value
                    if pd.notna(v):
                        v = v_dict.get(arg, lambda x: x)(v)

                    v_type = k_dict.get(arg, default_type)
                    if pd.notna(v) and v_type == 'string':
                        v = dumps(v)

                predicates[arg] = v

            if allow_empty or (predicates and None not in predicates.values()):
                new_predicates.append(Predicate(name, predicates))

        return PredicateResult(self, new_predicates)

    def get_predicates(self, name=None):
        if name:
            return [p for p in self.predicates if p.name == name]
        return self.predicates


    def format_predicates(self):
        return [str(p) + '\n' for p in self.predicates]

# TODO: documentation
class WikiData:
    """ wikidata.org interface """
    def __init__(self, format=JSON):
        user_agent = 'WikiData SPARQL interface'
        self.sparql = SPARQLWrapper('https://query.wikidata.org/bigdata/namespace/wdq/sparql', agent=user_agent)

    def query(self, q) -> Result:
        self.sparql.setQuery(q)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results_df = pd.json_normalize(results['results']['bindings'])

        return Result(results_df)


# TODO
class DatiCultura:
    """ dati.cultura.gov.it interface """
    def __init__(self, format=JSON):
        user_agent = 'DatiCultura SPARQL interface'
        self.sparql = SPARQLWrapper('https://dati.cultura.gov.it/sparql', agent=user_agent)

    def query(self, q) -> Result:
        self.sparql.setQuery(q)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results_df = pd.json_normalize(results['results']['bindings'])

        return Result(results_df)
