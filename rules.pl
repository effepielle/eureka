church_building("Q1754247", "Pisa Cathedral", 43.722664, 10.395996, "wheelchair accecbcbxcssible", 243045, "http://commons.wikimedia.org/wiki/Special:FilePath/Duomo%20of%20the%20Archdiocese%20of%20Pisa.jpeg").
church_building("Q1234534", "Chiesa Fibonacci", 43.234346, 10.37696, 243005, "http://commons.wikimedia.org/wiki/Special:FilePath/Duomo%20of%20the%20Archdiocese%20of%20Pisa.jpeg").
church_building("Q0034534", "Chiesa Fibonacci Accessibile", 43.234346, 10.37696, "wheelchair accessible", "http://commons.wikimedia.org/wiki/Special:FilePath/Duomo%20of%20the%20Archdiocese%20of%20Pisa.jpeg").
church_building("Q1754787", "Chiesa questo è un test", 93.722664, 10.395996, 247045, "http://commons.wikimedia.org/wiki/Special:FilePath/Duomo%20of%20the%20Archdiocese%20of%20Pisa.jpeg").
church_building("Q1354247", "Un altro testl", 43.722764, nan, "http://commons.wikimedia.org/wiki/Special:FilePath/Duomo%20of%20the%20Archdiocese%20of%20Pisa.jpeg").

indoor(Q,W,E,R,T,Y,I) :- church_building(Q,W,E,R, T,Y,I).
indoor(Q,W,E,R,T,Y) :- church_building(Q,W,E,R,T,Y).
indoor(Q,W,E,R,T) :- church_building(Q,W,E,R,T).
    wheelchair_accessible(X, Z, Y) :- church_building(X,Z,_,_,Y,_), \+number(Y), =(Y, "wheelchair accessible").
wheelchair_accessible(X, Z, Y) :- church_building(X,Z,_,_,Y,_), \+number(Y), =(Y, "wheelchair accessible").