
def checkCountry(loc_name):
    loc = str(loc_name).lower()
    eng = ['london' , 'uk', 'united kingdom' , 'liverpool', 'england','great britain']
    ita = ['rome' , 'italy' , 'italia' , 'milano' , 'roma' , 'torino' ,'firenze' , 'napoli','bologna', 'pisa', 'palermo'
          ,'genova', 'perugia' , 'lecce','livorno','verona','padova','bari','salerno','bergamo','cagliari','brescia','catania',
          'milan','rimini','modena','venezia','agrigento']
    
    
    us = ['u.s.','dallas','us', 'usa' , 'u.s.a' , 'orlando' , 'los angeles' , 'columbia' , 'greater hartford' , 'california' ,'new york',
         'united states', "alabama","alaska","arizona","arkansas","california","colorado",
          "connecticut","delaware","florida","georgia","hawaii","idaho","illinois",
          "indiana","iowa","kansas","kentucky","louisiana","maine","maryland",
          "massachusetts","michigan","minnesota","mississippi","missouri","montana",
          "nebraska","nevada","new hampshire","new jersey","new mexico","new york",
          "north carolina","north dakota","ohio","oklahoma","oregon","pennsylvania",
          "rhode island","south carolina","south dakota","tennessee","texas","utah",
          "vermont","virginia","washington","west virginia","wisconsin","wyoming", 'chicago', 'san francisco',
         'atlanta','norfolk area','wichita','memphis','boston','detroit','bay area','denver','san diego','tulsa','nashville'
          ,'cincinnati','charlotte','richmond','jersey','phoenix','seattle','philadelphia','louisville','seattle','oakland'
         ,'orange county','new orleans','portland','cleveland','miami','las vegas','victoria','saint louis'
          ,'mobile','middletown','tampa','san antonio','tucson','newark','albany','baltimore','jacksonville',
         'triad area','pittsburgh','honolulu','salt lake city','nj','nyc']
    
    
    asia = ['afghanistan', 'armenia', 'azerbaijan' , 'bahrain','bangladesh','bhutan','brunei',
            'cambodia','china','cyprus','georgia','india','indonesia','iran','iraq','israel','japan',
            'jordan', 'kazakhstan','kuwait','kyrgyzstan','laos','lebanon','malaysia','maldives','mongolia','myanmar',
            'burma', 'nepal','north korea','oman','pakistan','palestine','philippines','qatar', 'saudi arabia',
            'singapore','south korea','sri lanka','syria','taiwan','tajikistan','thailand','timor leste','turkey',
            'turkmenistan', 'united arab emirates', 'uae','uzbekistan' , 'vietnam' , 'yemen' , 'jakarta','new delhi',
           'cebu','mumbai','islamabad','baguio city','delhi','bandung','manila','phillipines']
    
    
    europe = ['albania','andorra','armenia','austria','belarus','belgium','bosnia and herzegovina','bulgaria'
             ,'bosnia','herzegovina','croatia','cyprus','czech republic','czech','denmark',
             'estonia','finland','france','georgia','germany','greece', 'hungary' , 'iceland'
             ,'ireland', 'kazakhstan','kosovo','latvia', 'liechtenstein','lithuania',
             'luxembourg','macedonia' , 'malta','moldova','monaco','poland','portugal','romania',
             'russia','san marino','serbia','slovakia','slovenia','spain','sweden','switzerland',
             'turkey','türkiye','ukraine','vatican','madrid','españa','paris','espana','barcelona','europe']
    
    
    america = ['antigua and barbuda','antigua','barbuda','st. john\'s','argentina','buenos aires',
              'bahamas','nassau','barbados','bridgetown','belize','belmopan','bolivia','sucre','brazil',
              'brasilia', 'sau paolo','rio de janeiro','canada','toronto','ottawa','chile','santiago',
              'colombia','bogota','costa rica','san josé','san jose','cuba','havana','dominica','roseau',
              'dominican republic','santo domingo','ecuador','quito','el salvador','san salvador','grenada','st. george\'s',
              'guatemala','guyana','georgetown','haiti','port-au-prince','port au prince',
              'honduras','tegucigalpa','jamaica','kingston','mexico','nicaragua','managua','panama',
              'paraguay','asunción','asuncion','peru','lima','trinidad and tobago','urugay','montevideo','venezuela','caracas',
              'brasil','são paulo','trinidad','puerto rico','méxico']
    oceania = ['australia','new zealand','wellington','sydney']
    
    
    if loc == 'nan' or loc == '':
        # nan value
        return 0
    #print(loc)
    #if ("rome" or "italy" or "italia" or "milano" or "roma") in loc:
    for option in ita:
        if option in loc:
            return 1 #italy
    
    for option in us:
        if option in loc:
            return 2 #Usa
   
    for option in asia:
        if option in loc:
            return 3 #asia + oceania
    for option in oceania:
        if option in loc:
            return 3 #asia + oceania
        
    for option in america:
        if option in loc:
            return 4
    
    for option in europe:
        if option in loc:
            return 5 #europe
    for option in eng:
        if option in loc:
            return 5 #europe
    return 6 #rest of the world
