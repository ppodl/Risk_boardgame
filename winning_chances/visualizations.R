library(dplyr)
library(ggplot2)

setwd('C:\\Users\\ppodl\\Desktop\\praca\\20230221_risk_boardgame')

df_risk <- 
  read.csv('odds_MOD.csv',sep=';',dec = ',')

?round

df_risk$win %>% round(2)

df_risk %>% 
  filter(att>1,win>0.1,win<0.9) %>%
  mutate(labels = (win %>% round(2))*100) %>% 
  ggplot(aes(x=att %>% as.factor(),y=def %>% as.factor(),fill=win)) +
    geom_tile() +
    geom_text(aes(label = labels) ) +
    scale_fill_gradient(low = 'darkred',high = 'darkgreen',guide = 'none') +
    theme_bw() +
    labs(x = 'number of attackers',
         y='number of defenders',
         title = 'Winning chances for attacker',
         subtitle = 'Risk boardgame, https://www.hasbro.com/common/instruct/risk.pdf',
         caption= 'created by Przemyslaw Podlasin,https://www.linkedin.com/in/przemyslaw-podlasin/') +
  theme(plot.title = element_text(size = 25)
        ,plot.subtitle = element_text(size = 20)
        ,panel.grid.major = element_line(colour = "darkgrey")
        ,axis.text = element_text(size = 15,colour = "black")
        ,axis.title = element_text(size = 12))


df_risk %>% 
  mutate(attacker_advantage = att - def) %>% 
  filter(attacker_advantage >= 0,attacker_advantage<6,att>1) %>%
  #filter(att==def) %>%
  ggplot(aes(x=att,y=win,color = attacker_advantage %>% as.factor(),group = attacker_advantage)) +
    geom_line() +
    geom_hline(yintercept = .5) +
    scale_color_manual(values = c('black','darkgrey','grey','lightblue','lightgreen','green')) +
    scale_x_continuous(breaks = 0:30,minor_breaks = NULL) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1),breaks = 1:10/10) + 
    geom_point() + 
    theme_bw() +
    labs(color = "attacker's advantage\n(attacking troops - defending troops)"
         ,title = 'Winning chances of attacker in Risk boardgame'
         ,x = "number of attacking troops") +
    theme(legend.position = "top")
  

