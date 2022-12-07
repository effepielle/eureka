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
    def function(self, name, *args) -> Result: 
        """ Fluent builder of n-ary functors """
        for _, row in self.df.iterrows():
            values = []
            for k in args:
                v = np.nan # TODO: why not use None?
                if k in self.df:
                    v = row[k]
                    if type(v) is str:
                        v = f'\"{v}\"'
                values.append(v) # TODO: why not use None?

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

