function [] = userMovieDistribution(csvFile)
  % pid,uid,helpN,helpD,score,time
  allData = csvread(csvFile, 1, 0);
  %x = allData(:, 1);
  y = allData(:, 2);
  %x = sort(x);
  hist(y);
  %{
  hist (y)
  figure(2)
  hist (x)

  [s, i] = sort(x);
  b = y(i, :);
  hist(b, x);
 %}

endfunction
