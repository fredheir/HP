require(memisc)
require(data.table)
require(ggplot2)
require(scales)

#Import data
data <- as.data.set(spss.system.file("CCES12_MIA_OUTPUT_20130621.sav"))
df = data.table(as.data.frame(data))

#Figure 4.3
temp=data.frame(table(df$MIA374))
temp$perc <- temp$Freq/sum(temp$Freq)
ggplot(temp,aes(Var1,perc))+geom_bar(stat='identity')+  
  scale_y_continuous(labels = percent_format())+
  ggtitle('Big events like wars, the current recession,and the outcomes of elections\n are controlled by small groups of people who are working in secret against the rest of us')



#Remove factor 6 or above to cut non response
#scores are subtracted from 6 to weight strongly agree as 5, strongly disagree as 1
#factorscore=loading1∗X1+loading2∗X2+…+loadingk∗Xk
df2=df[as.numeric(MIA380)<6&as.numeric(MIA379)<6&as.numeric(MIA381)<6]
df2[,conspScore:= 
      ((6-as.numeric(MIA379))*.836)+
      ((6-as.numeric(MIA380))*.818)+
      ((6-as.numeric(MIA381))*.865)
    ]

#Check that conpspScore correlates with variable V102 (it does not)
cor(df2$conspScore,df2$V102)

#Order by conspScore, assign bottom third as low, 
#middle third as medium, upper third as high
setkey(df2,conspScore)
df2$conspRating <- rep(c('1low','2medium','3high'),387)

#Check that low rating aligns with disagreement
head(df2[,c('conspScore','MIA379','MIA380','MIA381'),with=F])
#and that high rating aligns with agreement
tail(df2[,c('conspScore','MIA379','MIA380','MIA381'),with=F])

#Figure 4.7 (similar, often larger discrepancies for Figures 4.8, 4.10)
temp=data.table(data.frame(table(df2$conspRating,df2$gender)))
#Adjusting for larger number of female respondents
temp[Var2=='Female']$Freq=temp[Var2=='Female']$Freq*table(df2$gender)[1]/table(df2$gender)[2]
temp[,perc:=Freq/sum(Freq),by=Var1]
ggplot(temp,aes(Var1,perc,fill=Var2))+geom_bar(stat='identity',position="dodge")+  
  scale_y_continuous(labels = percent_format())

