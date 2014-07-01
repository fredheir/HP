def checkField(field,target):
    return db[targetDb].find({field:target}).count()==0