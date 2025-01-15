def diff(a,b, sensitivity = 2):
  sum = 0
  d = len(a)
  for i in range(d):
    sum += math.pow(abs(a[i]-b[i]),sensitivity)
  return round((math.pow(0.5,sum))/0.001)*0.001


  LOD = 8
  sum = 0
  for LOD in range(LOD,3,-1):
    guess = derivatives[e:LOD+e]
    combs = {i:derivatives[i:i+LOD] for i in range(len(derivatives)-LOD)}
    for index,comb in combs.items():
      difference = diff(comb,guess,2)
      sum += difference * derivatives[index + LOD] * (math.pow(0.5, 8-LOD))
