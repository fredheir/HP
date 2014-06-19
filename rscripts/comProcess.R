setwd("C:/Users/Rolf/Documents/c&d/HP")
d=read.csv("hpOut.txt",sep="\t",header=F,comment.char="")
dim(d)
colnames(d) <- c("id","timestamp","group","title","author","tags","nComments")
d$n <- 1:nrow(d)
require(data.table)
d$t <- as.numeric(as.character(d$timestamp))
table(d$t)
d <- data.table(d)
setkey(d,id)
d <- unique(d)
d[is.na(t)]

d$date <- as.Date(ymd(d$timestamp))
d <- d[!is.na(date)]
d$month <- floor_date(d$date,"month")
table(d$month)

d$count <- 1
artDat <- d

ggplot(d[year(date)>2012&group=="Crime"],aes(date,(nComments)))+geom_point()+geom_smooth(method="loess",span=.2)

gg <- d[nComments>0,list(
  n=sum(count),
  early=mean(nComments[date<as.Date("2013-08-08")]),
  late=mean(nComments[date>as.Date("2013-12-12")])  
        ),by=group]
gg <- gg[!is.na(early)]
gg <- gg[!is.na(late)]
gg$dif <- gg$early/gg$late
gg[n>200][order(-dif)]

d2 <- d[,list(n=sum(count),tot=sum(nComments)),by=timestamp]
d2[,mean:=tot/n]


require(ggplot2)
require(lubridate)
d2$date <- as.Date(ymd(d2$timestamp))
ggplot(d2[year(date)>2013&date<as.Date("2014-06-01")&n>10],aes(x=date,y=mean))+geom_point()+geom_smooth(method="loess",span=.1)+
  geom_vline(xintercept=as.numeric(as.Date("2013-12-10")),linetype=3, colour="black")+
  geom_vline(xintercept=as.numeric(as.Date("2013-08-22")),linetype=3, colour="black")+
  geom_vline(xintercept=as.numeric(as.Date("2013-09-01")),linetype=3, colour="black")+ylab("mean comment count")+ggtitle("Average comment numbers. Rule changes indicated by dotted line")


d[year(date)==2014&month(date)==06]

#===================COMMENT STATS

#entry_id= id of hp article
# _id = comment id
# parent id = comment replied to, 0 = comment to root
# user id = identification for user
# created at = timestamp
# nWords = number of words in comment
# typos = number of unrecognised words in message
# caps = number of all caps words
# nPunct= number of punctuation characters
# nNames = number of named entities
# nComma = number of commas
# nSent = number of sentences
# avSentLen = average number of words in sentence
# avWordLen = average number of characters per word
# nOffensive = number of possibly offensive words used
# avSyllables = estimated average number of syllables used
# threeSylPlys = ratio of words of length equal or greater to three syllables
setwd("C:/Users/Rolf/Documents/c&d/HP")
d=read.table("commentStats.txt",sep="\t",comment.char="",header=T)
d2 <- read.table("comments1")
d <- rbind(d,d2)
d$created_at = as.POSIXct(d$created_at,origin = "1970-01-01")
d2 <- d
write.table(d2,file="comments1")

d=data.table(d)
d$n <- 1:nrow(d)
d$day <- as.Date(floor_date(d$created_at,"day"))
d$count <- 1
d[,typos:=typos/nWords]
d[,caps:=caps/nWords]
d[,nPunct:=nPunct/nWords]
d[,nNames:=nNames/nWords]
d[,nComma:=nComma/nWords]
d[,nOffensive:=nOffensive/nWords]
d[,nNames:=nNames/nWords]
d[is.na(typos)] <- 0
d[is.na(caps)] <- 0
d[is.na(nPunct)] <- 0
d[is.na(nNames)] <- 0
d[is.na(nComma)] <- 0
d[is.na(nOffensive)] <- 0
d[is.na(nNames)] <- 0
cats=c("nWords","typos","caps","nPunct","nNames","nComma","nSent","avSentLen","avWordLen","nOffensive","avSyllables","threeSylPlus" )  

artDat$id <- as.numeric(as.character(artDat$id))
setkey(artDat,id)
setkey(d,X_id)
dd <- artDat[d]
dd <- dd[complete.cases(dd)]

d2 <- d[, lapply(.SD, mean, na.rm=TRUE), by=day,.SDcols= cats]
require(reshape2)

d3 <- melt(d2,id.vars=c("day"))
ggplot(d3[year(day)>2012],aes(day,value))+geom_point()+geom_smooth()+geom_smooth(method="lm")+facet_wrap(~variable,scales="free")+geom_vline(xintercept=as.numeric(as.Date("2013-12-10")),linetype=3, colour="black")+  geom_vline(xintercept=as.numeric(as.Date("2014-06-06")),linetype=3, colour="black")+geom_smooth(method="lm")


> prop.table(table(d$nWords>100,d$day>as.Date("2013-12-10")),margin=2)

sd(d[day>as.Date("2013-12-10")]$nNames)
sd(d[day<as.Date("2013-12-10")]$nNames)

d2 <- d[,list(v1=mean(nNames/nWords),n=sum(count)),by=day]
d2 <- d[,list(v1=mean(avSyllables),n=sum(count)),by=day]
ggplot(d2[year(day)>2012&n>10],aes(day,v1))+geom_point()+geom_smooth()+geom_vline(xintercept=as.numeric(as.Date("2013-12-10")),linetype=3, colour="black")+  geom_vline(xintercept=as.numeric(as.Date("2014-06-08")),linetype=3, colour="black")+geom_smooth(method="lm")


