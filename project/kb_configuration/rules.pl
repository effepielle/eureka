%use table to store same facts repeated
% if infinite loop, uncomment (dynamic program like fix)  :- table label/2,position/3,type/2,star/2,image/2,trip_advisor/2.

% query like ?-site_star(Label,Image,Rating) ;
% site_star(Label,Rating). to retrieve cultural assets without image

is_type(Label,Category):-
    label(Id,Label),type(Id,Category).


site_star(Label,Image,Rating):-
    label(Id,Label), image(Id,Image), star(Id,Rating).
site_star(Label,Rating):-
    label(Id,Label), star(Id,Rating).


is_wheelchair_friendly(Label,Image):-
    label(Id,Label), image(Id,Image), wheelchair_friendly(Id).
is_wheelchair_friendly(Label):-
    label(Id,Label), wheelchair_friendly(Id).


is_wheelchair_unfriendly(Label,Image):-
    label(Id,Label), image(Id,Image), \+wheelchair_friendly(Id).
is_wheelchair_unfriendly(Label):-
    label(Id,Label), \+wheelchair_friendly(Id).

site_cost(Label,Image,Cost) :- 
    label(Id,Label), image(Id,Image), ticket_cost(Id,Cost).
site_cost(Label,Cost) :- 
    label(Id,Label), ticket_cost(Id,Cost).

site_timetable(Label,Image, Day, Opening, Closing) :- 
    label(Id,Label), image(Id,Image), timetable_info(Id,Day,Opening, Closing).
site_timetable(Label,Day,Opening,Closing) :- 
    label(Id,Label), timetable_info(Id,Day,Opening, Closing).

%composing the type of result
% do an and query with is_wheelchair_friendly or
% is_wheelchair_unfriendly if you want to know also the accessibility
%info
% missing trip_advisor
recommended_cultural_asset(Label, Lat, Lon, Trip_advisor,Image,Rating):-
    label(Id,Label), position(Id, Lat, Lon), trip_advisor(Id,Trip_advisor),
    site_star(Label,Image,Rating).
recommended_cultural_asset(Label, Lat, Lon,Image,Rating):-
    label(Id,Label), position(Id, Lat, Lon), site_star(Label,Image,Rating).
recommended_cultural_asset(Label, Lat, Lon,Rating):-
    label(Id,Label), position(Id, Lat, Lon), site_star(Label,Rating).


%various filter on result
filter_by_star(Label,Image,Rating,Threshold):-
    site_star(Label,Image,Rating), Rating>=Threshold.
filter_by_star(Label,Rating,Threshold):-
    site_star(Label,Rating), Rating>=Threshold.

filter_by_cost(Label, Image, Cost, Threshold) :-
    site_cost(Label, Image, Cost), Cost>=Threshold.
filter_by_cost(Label, Cost, Threshold) :-
    site_cost(Label, Cost), Cost>=Threshold.

free_entry(Label, Image, Cost) :-
    site_cost(Label, Image, Cost), Cost=0.0.
free_entry(Label, Cost) :-
    site_cost(Label, Cost), Cost=0.0.

filter_by_timetable(Label, Image, Day, Opening, Closing, Time) :-
    site_timetable(Label,Image,Day,Opening,Closing), Time>=Opening, Time=<Closing.
filter_by_timetable(Label, Day, Opening, Closing, Time) :-
    site_timetable(Label,Day,Opening,Closing), Time>=Opening, Time=<Closing.


%if indoor or outdoor
indoor(Label,Image):-
    label(Id,Label), image(Id,Image), (
        type(Id,"church_building"); type(Id, "library"); type(Id, "palace");
        type(Id, "theater"); type(Id, "arts_venue"); type(Id,"museum")).
indoor(Label):-
    label(Id,Label), (
        type(Id,"church_building"); type(Id, "library"); type(Id, "palace");
        type(Id, "theater"); type(Id, "arts_venue"); type(Id,"museum")).


outdoor(Label,Image):-
    label(Id,Label), image(Id,Image), (
        type(Id,"park"); type(Id,"public_garden"); type(Id,"city_walls");
        type(Id,"monument"); type(Id, "tower"); type(Id, "city_gate");
        type(Id, "bridge"); type(Id, "cemetery"); type(Id,"square")).
outdoor(Label):-
    label(Id,Label), (
        type(Id,"park"); type(Id,"public_garden"); type(Id,"city_walls");
        type(Id,"monument"); type(Id, "tower"); type(Id, "city_gate");
        type(Id, "bridge"); type(Id, "cemetery"); type(Id,"square")).


%if raining
visitable_if_raining(Label,Image):-
    indoor(Label,Image).
visitable_if_raining(Label):-
    indoor(Label).


visitable_if_good_weather(Label,Image):-
    outdoor(Label, Image); indoor(Label, Image).
visitable_if_good_weather(Label):-
    outdoor(Label); indoor(Label).
