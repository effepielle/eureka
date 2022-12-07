from __future__ import annotations
import numpy as np
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# TODO: documentation
class Term:
    """ N-ary compound term: functor_name(v1, v2, ..., vN) """
    def __init__(self, name, term_dict):
        self.name = name
        self.term_dict = term_dict

    def project(self, keys):
        return Term(self.name,
                {k: v for k, v in self.term_dict.items() if k in keys})

    def hide(self, keys):
        return Term(self.name,
                {k: v for k, v in self.term_dict.items() if k not in keys})

    def __str__(self) -> str:
        arg_str = ','.join(map(str, self.term_dict.values()))
        return f"{self.name}({arg_str})."

# TODO: documentation
class Result:
    """ Simple data wrapper holding query results """
    def __init__(self, df):
        self.df = df
        self.terms = []

    def predicate(self, name, pred, *args, hidden=[], **kwargs) -> Result:
        """ Fluent builder of n-ary predicates """
        return self.function(name, *args, pred = pred, hidden=hidden, **kwargs)

    def function(self, name, *args, **kwargs) -> Result: 
        """ Fluent builder of n-ary functors """

        # TODO: move to function definition
        k_dict = kwargs.get('k_dict', {})
        v_dict = kwargs.get('v_dict', {})
        allow_empty = kwargs.get('allow_empty', False)
        default_type = kwargs.get('default_type', 'string')
        pred = kwargs.get('pred', None)
        hidden = kwargs.get('hidden', [])

        # concatenate keys and remove duplicates while preserving order
        args = list(dict.fromkeys(list(args) + list(k_dict.keys())))

        assert all(type(arg) in [str] for arg in args)

        for _, row in self.df.iterrows():
            terms = {}
            for arg in args:
                k = f"{arg}.value"
                v = None
                if k in self.df:
                    v = row[k]
                    v = v if pd.notna(v) else None # TODO: remove if nan is needed

                    # apply optional computation to the value
                    if v and pd.notna(v):
                        v = v_dict.get(arg, lambda x: x)(v)

                    v_type = k_dict.get(arg, default_type)
                    if v and pd.notna(v) and v_type == 'string':
                        v = f'\"{v}\"'

                terms[arg] = v

            if pred is None or pred(terms):
                if allow_empty or (terms and None not in terms.values()):
                    self.terms.append(Term(name, terms).hide(hidden))


        return self


    def format_terms(self):
        return [str(term) + '\n' for term in self.terms]

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
    def __init__(self):
        pass

