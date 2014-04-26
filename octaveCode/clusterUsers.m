function [] = clusterUsers(avgsFile)

  data = csvread(avgsFile);
size(data, 1) % check that all was read
[idx, centers] = kmeans2(data, 8);

## Plot the result
 figure
plot (data (idx==1, 1), 'ro');
 hold on
 plot (data (idx==2, 1), 'bs');
 plot (data (idx==3, 1), 'gs');
 plot (data (idx==4, 1), 'ms');
 plot (data (idx==5, 1), 'cs');
 plot (data (idx==6, 1), 'g+');
 plot (data (idx==7, 1), 'r+');
 plot (data (idx==8, 1), 'b+');
plot (centers (:, 1), 'kv', 'markersize', 10);
 hold off


endfunction
