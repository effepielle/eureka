:-include("rules.pl").

%following are templates facts, delete them when you are sure to feed the KB with wikidata in the exact same way:
%of course the facts exists only when corresponding features in wikidata or dati.cultura.gov.it are actually instantiated, otherwise not.
%constraint: id, label, type and position MUST exist to keep in KB a wikidata entity !


%label of corresponding wikidata id
label("Q4011005","Viale delle Piagge (Pisa)").
label("Q3678366","Cittadella Nuova").

% type of each wikidata id, corresponding to label of each class in
% sparql query
type("Q4011005","park").
type("Q3678366","public_garden").

position("Q4011005",43.7053, 10.4202).
position("Q3678366", 43.710406, 10.406252).

wheelchair_friendly("Q3678366").

%trip advisor id from wikidata
trip_advisor("Q4011005", 10638421).

star("Q4011005",5).
star("Q3678366",4).


image("Q4011005","http://commons.wikimedia.org/wiki/Special:FilePath/Pisa%2C%202015%2C%20Viale%20delle%20Piagge.jpg").

