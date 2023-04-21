%utilities to help to compose final recommendation
site_label(Label):-
    label(_,Label).

site_position(Label, Lat, Lon):-
    label(Id, Label), position(Id, Lat, Lon).

site_star(Label,Rating):-
    label(Id,Label), star(Id,Rating).
site_star(Label,Rating):-
    label(Id,Label), star(Id,Rating).

is_type(Label,Category):-
    label(Id,Label),type(Id,Category).

site_image(Label, Image):-
    label(Id, Label), image(Id, Image).

site_tripadvisor(Label, TripID):-
    label(Id, Label), trip_advisor(Id, TripID).

site_cost(Label,Cost) :-
    label(Id,Label), ticket_cost(Id,Cost).

site_timetable(Label, Day, Opening, Closing) :- label(Id,Label), timetable_info(Id,Day,Opening, Closing).

weekday(Day) :- (Day="monday";Day="tuesday";Day="wednesday";Day="thursday"; Day="friday";Day="saturday").

holiday(Day) :- \+weekday(Day).

%core composition rules
site_mandatory_info(Label,Lat,Lon,Rating) :-  site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating).

%optional filter with xor (only empty result or only full result)
site_optional_info(Label, Image, TripID, Cost) :- site_label(Label),
    ((site_image(Label, Image) , \+Image = "" ) ; (\+site_image(Label, Image) , Image = "" )),
( (site_tripadvisor(Label, TripID) , \+TripID = "") ; (\+site_tripadvisor(Label, TripID) , TripID = "") ),
( (site_cost(Label, Cost) , \+Cost = -1.0) ; (\+site_cost(Label, Cost), Cost = -1.0)).

%rules to directly compose the final recommendation
recommended_cultural_asset(Label, Lat, Lon, Rating, Image, TripID, Cost):- site_mandatory_info(Label,Lat,Lon,Rating), site_optional_info(Label, Image, TripID, Cost).


%filters to apply to final recommendation
filter_by_star(Label,Rating,Threshold):-
    site_star(Label,Rating), Rating>=Threshold.

filter_by_cost(Label, Cost, Threshold) :-
    site_cost(Label, Cost), Cost>=Threshold.

filter_by_cost(Label, Cost, Lower_Threshold, Upper_Threshold) :-
    site_cost(Label, Cost), Cost=<Upper_Threshold, Cost>=Lower_Threshold.

free_entry(Label, Cost) :-
    site_cost(Label, Cost), Cost=0.0.

filter_by_timetable(Label, Day, Opening, Closing, Selected_opening, Selected_closing) :-
    site_timetable(Label,Day,Opening,Closing), Selected_opening>=Opening, Selected_closing=<Closing.


is_wheelchair_friendly(Label):-
    label(Id,Label), wheelchair_friendly(Id).

is_wheelchair_unfriendly(Label):-
    label(Id,Label), \+wheelchair_friendly(Id).

is_indoor(Label):-
    site_label(Label),
    (is_type(Label,"church_building"); is_type(Label, "library"); is_type(Label, "palace");
    is_type(Label, "theater"); is_type(Label, "arts_venue"); is_type(Label,"museum")).

is_outdoor(Label):-
    site_label(Label),
    (is_type(Label,"park"); is_type(Label,"public_garden"); is_type(Label,"city_walls");
    is_type(Label,"monument"); is_type(Label, "tower"); is_type(Label, "city_gate");
    is_type(Label, "bridge"); is_type(Label, "cemetery"); is_type(Label,"square")).

visitable_if_raining(Label):-
    is_indoor(Label).

%KB evaluation rule, for test purposes only
site_optional_info(Label, Image, TripID) :- site_label(Label),
    ((site_image(Label, Image) , \+Image = "" ) ; (\+site_image(Label, Image) , Image = "" )),
( (site_tripadvisor(Label, TripID) , \+TripID = "") ; (\+site_tripadvisor(Label, TripID) , TripID = "") ).























