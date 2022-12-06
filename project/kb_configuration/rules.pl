%TODO add more categories
    %partition by categories
arts_and_culture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- museum(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).
architecture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- city_walls(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star); church_building(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                                    square(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);monument(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).
green_areas(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- park(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star); public_garden(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).

indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- church_building(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                       museum(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).

outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- green_areas(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star); city_walls(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                        monument(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);square(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).

%wheelchair_accessible(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- Accessibility = "wheelchair accessible", (arts_and_culture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star);
%                                                                                                                architecture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star); green_areas(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star)).

visitable_if_raining(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image , Star).

%variable threshold settable by user
best_site(Id,Label,Lat,Lon,Accessibility,TripId,Image,Star) :- arts_and_culture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star), Site_star >= Star.
best_site(Id,Label,Lat,Lon,Accessibility,TripId,Image,Star) :- architecture(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star) , Site_star >= Star.
best_site(Id,Label,Lat,Lon,Accessibility,TripId,Image,Star) :-  green_areas(Id,Label,Lat,Lon,Accessibility,TripId,Image, Site_star), Site_star >= Star.
    %same as best_site will be also the cost (imposing a threshold)