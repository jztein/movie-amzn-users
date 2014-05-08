function [] = relateScores(csvFile)

  scores = csvread(csvFile)
  figure(1)
  hist(scores, bins=5)
  print("scoresHist_oct.png", "-dpng")
