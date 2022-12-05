indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- church_building(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                       museum(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).

outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- park(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                        public_garden(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                        city_walls(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star);
                                                        monument(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star).

wheelchair_accessible(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- Accessibility = "wheelchair accessible", (indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star); 
                                                                                                                outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star)).

visitable_if_raining(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star) :- indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image , Star).

    %not interested in other information while querying for best cultural site
best_site(Id,Label,Lat,Lon,Accessibility,TripId,Image,Star) :- (indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star); outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image, Star)), Star >=4.
