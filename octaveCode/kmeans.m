function [classes, centers, sumd, D] = kmeans (data, k, varargin)
										  [reg, prop] = parseparams (varargin);
% defaults for options
emptyaction = "error";
start = "sample";
  #used for getting the number of samples
nRows = rows (data);
  ## used to hold the distances from each sample to each class
  D = zeros (nRows, k);
  #used for convergence of the centroids
err = 1;
  #initial sum of distances
sumd = Inf;
## Input checking, validate the matrix and k
  if (!isnumeric (data) || !ismatrix (data) || !isreal (data))
    error ("kmeans: first input argument must be a DxN real data matrix");
elseif (!isscalar (k))
error ("kmeans: second input argument must be a scalar");
  endif
  if (length (varargin) > 0)
    ## check for the ‘emptyaction’ property
    found = find (strcmpi (prop, "emptyaction") == 1);
switch (lower (prop{found+1}))
      case "singleton"
        emptyaction = "singleton";
      otherwise
      error ("kmeans: unsupported empty cluster action parameter");
    endswitch
  endif
  ## check for the ‘start’ property
  switch (lower (start))
    case "sample"
      idx = randperm (nRows) (1:k);
centers = data (idx, :);
    otherwise
    error ("kmeans: unsupported initial clustering parameter");
  endswitch
  ## Run the algorithm
  while err > .001
    ## Compute distances
  for i = 1:k
	    D (:, i) = sumsq (data – repmat (centers(i, :), nRows, 1), 2);
    endfor
    ## Classify
    [tmp, classes] = min (D, [], 2);
    ## Calculate new centroids
    for i = 1:k
      ## Get binary vector indicating membership in cluster i
	      membership = (classes == i);
      ## Check for empty clusters
      if (sum (membership) == 0)
        switch emptyaction
	## if ‘singleton’, then find the point that is the
          ## farthest and add it to the empty cluster
          case "singleton"
	idx=maxCostSampleIndex (data, centers(i,:));
classes(idx) = i;
membership(idx)=1;
         ## if ‘error’ then throw the error
          otherwise
	 error ("kmeans: empty cluster created");
        endswitch
     endif ## end check for empty clusters
      ## update the centroids
     members = data(membership, :);
centers(i, :) = sum(members,1)/size(members,1);
    endfor
    ## calculate the difference in the sum of distances
    err  = sumd – objCost (data, classes, centers);
    ## update the current sum of distances
    sumd = objCost (data, classes, centers);
  endwhile
endfunction
## calculate the sum of distances
  function obj = objCost (data, classes, centers)
    obj = 0;
for i=1:rows (data)
	obj = obj + sumsq (data(i,:) – centers(classes(i),:));
    endfor
endfunction
    function idx = maxCostSampleIndex (data, centers)
      cost = 0;
for idx = 1:rows (data)
	    if cost < sumsq (data(idx,:) – centers)
	    cost = sumsq (data(idx,:) – centers);
    endif
  endfor
endfunction
%!demo
%! ## Generate a two-cluster problem
    %! C1 = randn (100, 2) + 1;
%! C2 = randn (100, 2) – 1;
%! data = [C1; C2];
%!
%! ## Perform clustering
%! [idx, centers] = kmeans (data, 2);
%!
%! ## Plot the result
%! figure
%! plot (data (idx==1, 1), data (idx==1, 2), ‘ro’);
%! hold on
%! plot (data (idx==2, 1), data (idx==2, 2), ‘bs’);
%! plot (centers (:, 1), centers (:, 2), ‘kv’, ‘markersize’, 10);
%! hold off
