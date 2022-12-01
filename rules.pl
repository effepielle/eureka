indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image) :- church_building(Id,Label,Lat,Lon,Accessibility,TripId,Image);
                                                       museum(Id,Label,Lat,Lon,Accessibility,TripId,Image).

outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image) :- park(Id,Label,Lat,Lon,Accessibility,TripId,Image);
                                                        public_garden(Id,Label,Lat,Lon,Accessibility,TripId,Image);
                                                        city_walls(Id,Label,Lat,Lon,Accessibility,TripId,Image);
                                                        monument(Id,Label,Lat,Lon,Accessibility,TripId,Image).

wheelchair_accessible(Id,Label,Lat,Lon,Accessibility,TripId,Image) :- Accessibility = "wheelchair accessible", (indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image); 
                                                                                                                outdoor(Id,Label,Lat,Lon,Accessibility,TripId,Image)).

visitable_if_raining(Id,Label,Lat,Lon,Accessibility,TripId,Image) :- indoor(Id,Label,Lat,Lon,Accessibility,TripId,Image).