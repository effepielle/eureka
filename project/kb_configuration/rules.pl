%use table to store same facts repeated
% if infinite loop, uncomment (dynamic program like fix)  :- table label/2,position/3,type/2,star/2,image/2,trip_advisor/2.

% query like ?-site_star(Label,Image,Rating) ;
% site_star(Label,Rating). to retrieve cultural assets without image

%utilities
is_type(Label,Category):-
    label(Id,Label),type(Id,Category).

site_label(Label):-
    label(_,Label).

site_image(Label, Image):-
    label(Id, Label), image(Id, Image).

site_position(Label, Lat, Lon):-
    label(Id, Label), position(Id, Lat, Lon).

site_tripadvisor(Label, TripID):-
    label(Id, Label), trip_advisor(Id, TripID).

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
recommended_cultural_asset(Label, Lat, Lon, Rating, Image, TripID, Day, Opening, Closing, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_timetable(Label, Image, Day, Opening, Closing), site_cost(Label, Image, Cost).

recommended_cultural_asset(Label, Lat, Lon, Rating, Image, TripID, Day, Opening, Closing):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_timetable(Label, Image, Day, Opening, Closing).
recommended_cultural_asset(Label, Lat, Lon, Rating, Image, Day, Opening, Closing, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_timetable(Label, Image, Day, Opening, Closing), site_cost(Label, Image, Cost).
recommended_cultural_asset(Label, Lat, Lon, Rating, TripID, Day, Opening, Closing, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_timetable(Label, Day, Opening, Closing), site_cost(Label, Cost).

recommended_cultural_asset(Label, Lat, Lon, Rating, Image, Day, Opening, Closing):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_timetable(Label, Image, Day, Opening, Closing).
recommended_cultural_asset(Label, Lat, Lon, Rating, TripID, Day, Opening, Closing):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_timetable(Label, Day, Opening, Closing).
recommended_cultural_asset(Label, Lat, Lon, Rating, Day, Opening, Closing, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_timetable(Label, Day, Opening, Closing), site_cost(Label,Cost).

recommended_cultural_asset(Label, Lat, Lon, Rating, Image, TripID, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_cost(Label, Image, Cost).
recommended_cultural_asset(Label, Lat, Lon, Rating, Day, Opening, Closing):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_timetable(Label, Day, Opening, Closing).

recommended_cultural_asset(Label, Lat, Lon, Rating, Image, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_cost(Label, Image, Cost).
recommended_cultural_asset(Label, Lat, Lon, Rating, TripID, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_tripadvisor(Label, TripID), site_cost(Label, Cost).

recommended_cultural_asset(Label, Lat, Lon, Rating, Cost):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating), site_cost(Label, Cost).
recommended_cultural_asset(Label, Lat, Lon, Image, Rating):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Image, Rating).

recommended_cultural_asset(Label, Lat, Lon, Rating):-
    site_label(Label), site_position(Label, Lat, Lon), site_star(Label, Rating).


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
    site_label(Label), site_image(Label, Image), (
        is_type(Label,"church_building"); is_type(Label, "library"); is_type(Label, "palace");
        is_type(Label, "theater"); is_type(Label, "arts_venue"); is_type(Label,"museum")).
indoor(Label):-
    site_label(Label), (
        is_type(Label,"church_building"); is_type(Label, "library"); is_type(Label, "palace");
        is_type(Label, "theater"); is_type(Label, "arts_venue"); is_type(Label,"museum")).


outdoor(Label,Image):-
    site_label(Label), site_image(Label, Image), (
        is_type(Label,"park"); is_type(Label,"public_garden"); is_type(Label,"city_walls");
        is_type(Label,"monument"); is_type(Label, "tower"); is_type(Label, "city_gate");
        is_type(Label, "bridge"); is_type(Label, "cemetery"); is_type(Label,"square")).
outdoor(Label):-
    site_label(Label), (
        is_type(Label,"park"); is_type(Label,"public_garden"); is_type(Label,"city_walls");
        is_type(Label,"monument"); is_type(Label, "tower"); is_type(Label, "city_gate");
        is_type(Label, "bridge"); is_type(Label, "cemetery"); is_type(Label,"square")).


%if raining
visitable_if_raining(Label,Image):-
    indoor(Label,Image).
visitable_if_raining(Label):-
    indoor(Label).


visitable_if_good_weather(Label,Image):-
    outdoor(Label, Image); indoor(Label, Image).
visitable_if_good_weather(Label):-
    outdoor(Label); indoor(Label).
