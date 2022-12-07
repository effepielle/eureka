from __future__ import annotations
import numpy as np
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

class Term:
    """ N-ary compound term: functor_name(v1, v2, ..., vN) """
    def __init__(self, name, *values):
        self.name = name
        self.values = values

    def __str__(self) -> str:
        arg_str = ','.join(map(str, self.values))
        return f"{self.name}({arg_str})."

class Result:
    """ Simple data wrapper holding query results """
    def __init__(self, df):
        self.df = df
        self.terms = []

    # TODO: make args optionally callable (for custom computations on keys)
    def function(self, name, *args, **kwargs) -> Result: 
        """ Fluent builder of n-ary functors """

        k_dict = kwargs.get('k_dict', {})
        v_dict = kwargs.get('v_dict', {})
        default_type = kwargs.get('default_type', 'string')

        args = set(args).union(k_dict.keys())

        assert all(type(arg) in [str] for arg in args)

        for _, row in self.df.iterrows():
            values = []
            for arg in args:
                k = f"{arg}.value"
                # v = np.nan
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


                values.append(v)

            self.terms.append(Term(name, *values))

        return self

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

