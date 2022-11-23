options(warn=-1)
# library(OutrankingTools)
Electre3_SimpleThresholds <- function (performanceMatrix, alternatives, criteria, minmaxcriteria, 
                                       criteriaWeights, IndifferenceThresholds, PreferenceThresholds, 
                                       VetoThresholds, mode_def = NULL) 
{
  print("STARTING")
  # cat("\f")
  if (is.null(dim(performanceMatrix))){
    print("e1")
      stop("less than 2 criteria or 2 alternatives")
  }
  if (!((is.matrix(performanceMatrix) || (is.data.frame(performanceMatrix))))){ 
    print("e2")
    stop("wrong performanceMatrix, should be a matrix or a data frame")
  }
  if (!(is.vector(alternatives))) {
    print("e3")
    stop("alternatives should be a vector")
  }
   
    
  if (!is.character(alternatives)) {
    print("e4")
   
    stop("alternatives should be a character vector")
    }
  if (!(nrow(performanceMatrix) == length(alternatives))) 
  {
    print("e5")
    stop("length of alternatives should be checked")
  }
  if (!(is.vector(criteria))) 
  {
    print("e6")
    stop("criteria should be a vector")
  }
  if (!is.character(criteria)) {
    print("e7")
    stop("criteria should be a character vector")
  }
  if (!(ncol(performanceMatrix) == length(criteria))) 
  {
    print("e8")
    stop("length of criteria should be checked")
  }
  if (!(is.vector(minmaxcriteria))) {
    print("e9")
    stop("minmaxcriteria should be a vector")
  }    
  minmaxcriteria = tolower(minmaxcriteria)
  if (!(ncol(performanceMatrix) == length(minmaxcriteria))){
    print("e10")
    print(minmaxcriteria) 
    stop("length of minmaxcriteria should be checked")
  }  
  n = length(minmaxcriteria)
  for (i in 1:n) {
    if (!((minmaxcriteria[i] == "min") || (minmaxcriteria[i] == 
                                           "max"))) {
      print("e11") 
      stop(" Vector minmaxcriteria must contain 'max' or 'min' ")
    }
  }
  if (!(is.vector(criteriaWeights))) 
    stop("criteriaWeights should be a vector")
  if (!is.numeric(criteriaWeights)) 
    stop("criteriaWeights should be a numeric vector")
  if (!(ncol(performanceMatrix) == length(criteriaWeights))) 
    stop("length of criteriaWeights should be checked")
  if (!(is.vector(IndifferenceThresholds))) 
    stop("IndifferenceThresholds should be a vector")
  if (!(ncol(performanceMatrix) == length(IndifferenceThresholds))) 
    stop("length of IndifferenceThresholds should be checked")
  if (!(is.vector(PreferenceThresholds))) 
    stop("PreferenceThresholds should be a vector")
  if (!(ncol(performanceMatrix) == length(PreferenceThresholds))) 
    stop("length of PreferenceThresholds should be checked")
  if (!(is.vector(VetoThresholds))) 
    stop("VetoThresholds should be a vector")
  if (!(ncol(performanceMatrix) == length(VetoThresholds))) 
    stop("length of VetoThresholds should be checked")
  if (is.null(mode_def)) {
    mode_def = c(rep("D", times = ncol(performanceMatrix)))
  }
  if (!(is.vector(mode_def))) 
    stop("mode_def should be a vector")
  mode_def = toupper(mode_def)
  if (!(ncol(performanceMatrix) == length(mode_def))) 
    stop("length of mode_def should be checked")
  n = length(mode_def)
  for (i in 1:n) {
    if (!((mode_def[i] != "I") || (mode_def[i] != "D"))) {
      stop(" Vector mode_def must contain 'I' or 'D'")
    }
  }
  
  
  etape_asc <- function(newmat, to_rank, c_bar, alpha, beta) {
    newmat_e = newmat
    newmat_0 = newmat
    to_rank_e = to_rank
    to_rank_0 = to_rank
    ind_min_lq = to_rank_e
    lambda_1 = 1
    etap = 1
    beta = 0.3
    alpha = 0.15
    lambda_10 = 0
    c_bar_e = list()
    len_ind_min_lq = length(ind_min_lq)
    stop = 0
    while ((len_ind_min_lq > 1) && (lambda_1 > 0)) {
      # cat(paste("Etape ", etap, sep = ""), "\n")
      to_rank_e = rownames(newmat_e)
      to_rank_e = setdiff(to_rank_0, names(ind_min_lq))
      fomn = rownames(newmat_e)
      m = nrow(newmat_e)
      newmat_i = newmat_e
      diag(newmat_i) = 0
      vec_mat_cred = as.vector(newmat_i)
      v_m_c = rev(sort(vec_mat_cred))
      if (etap == 1) {
        lambda_0 = max(v_m_c)
      }
      else {
        lambda_0 = lambda_10
      }
      lambda = lambda_0 - (0.3 - 0.15 * lambda_0)
      v_m_c = v_m_c[v_m_c < lambda]
      if (length(v_m_c) == 0) {
        lambda_1 = 0
      }
      else {
        lambda_1 = max(v_m_c)
      }
      mat_rel_cred <- matrix(rep(0, m * m), m, m)
      for (i in 1:m) {
        for (j in 1:m) {
          if ((newmat_e[i, j] > lambda_1) && (newmat_e[i, 
                                                       j] > (newmat_e[j, i] + (0.3 - 0.15 * newmat_e[i, 
                                                                                                     j])))) {
            mat_rel_cred[i, j] = 1
          }
          else {
            mat_rel_cred[i, j] = 0
          }
        }
      }
      colnames(mat_rel_cred) = fomn
      rownames(mat_rel_cred) = fomn
      lambda_p = c(rep(0, m))
      lambda_f = c(rep(0, m))
      lambda_q = c(rep(0, m))
      lambda_p = apply(mat_rel_cred, 1, sum)
      lambda_f = apply(mat_rel_cred, 2, sum)
      lambda_q = lambda_p - lambda_f
      v_min_lq = min(lambda_q)
      ind_min_lq = which(lambda_q == v_min_lq)
      name_ind_min_lq = names(ind_min_lq)
      len_ind_min_lq = length(ind_min_lq)
      if (len_ind_min_lq == 1) {
        c_bar_e = name_ind_min_lq
      }
      else {
        c_bar_e = name_ind_min_lq
        newmat_e = newmat_e[match(name_ind_min_lq, rownames(newmat_e)), 
                            match(name_ind_min_lq, colnames(newmat_e))]
      }
      # cat("----------------------------------------------------", 
      #     "\n")
      # cat("Etap's ranking.", "\n")
      # cat("----------------------------------------------------", 
      #     "\n")
      # print(c_bar_e)
      # cat("----------------------------------------------------", 
      #     "\n")
      lambda_10 = lambda_1
      len_ind_min_lq == length(c_bar_e)
      etap = etap + 1
    }
    c_bar = c_bar_e
    new_mat = newmat_0[-match(c_bar_e, rownames(newmat_0)), 
                       match(c_bar_e, colnames(newmat_0))]
    to_rank = rownames(newmat)
    return(list(newmat = newmat, to_rank = to_rank, c_bar = c_bar))
  }
  etape_dsc <- function(newmat, to_rank, c_bar, alpha, beta) {
    newmat_e = newmat
    newmat_0 = newmat
    to_rank_e = to_rank
    to_rank_0 = to_rank
    ind_max_lq = to_rank_e
    lambda_1 = 1
    etap = 1
    beta = 0.3
    alpha = 0.15
    lambda_10 = 0
    c_bar_e = list()
    len_ind_max_lq = length(ind_max_lq)
    stop = 0
    while ((len_ind_max_lq > 1) && (lambda_1 > 0)) {
      # cat(paste("Etape ", etap, sep = ""), "\n")
      to_rank_e = rownames(newmat_e)
      to_rank_e = setdiff(to_rank_0, names(ind_max_lq))
      fomn = rownames(newmat_e)
      m = nrow(newmat_e)
      newmat_i = newmat_e
      diag(newmat_i) = 0
      vec_mat_cred = as.vector(newmat_i)
      v_m_c = rev(sort(vec_mat_cred))
      if (etap == 1) {
        lambda_0 = max(v_m_c)
      }
      else {
        lambda_0 = lambda_10
      }
      lambda = lambda_0 - (0.3 - 0.15 * lambda_0)
      v_m_c = v_m_c[v_m_c < lambda]
      if (length(v_m_c) == 0) {
        lambda_1 = 0
      }
      else {
        lambda_1 = max(v_m_c)
      }
      mat_rel_cred <- matrix(rep(0, m * m), m, m)
      for (i in 1:m) {
        for (j in 1:m) {
          if ((newmat_e[i, j] > lambda_1) && (newmat_e[i, 
                                                       j] > (newmat_e[j, i] + (0.3 - 0.15 * newmat_e[i, 
                                                                                                     j])))) {
            mat_rel_cred[i, j] = 1
          }
          else {
            mat_rel_cred[i, j] = 0
          }
        }
      }
      colnames(mat_rel_cred) = fomn
      rownames(mat_rel_cred) = fomn
      lambda_p = c(rep(0, m))
      lambda_f = c(rep(0, m))
      lambda_q = c(rep(0, m))
      lambda_p = apply(mat_rel_cred, 1, sum)
      lambda_f = apply(mat_rel_cred, 2, sum)
      lambda_q = lambda_p - lambda_f
      v_max_lq = max(lambda_q)
      ind_max_lq = which(lambda_q == v_max_lq)
      name_ind_max_lq = names(ind_max_lq)
      len_ind_max_lq = length(ind_max_lq)
      if (len_ind_max_lq == 1) {
        c_bar_e = name_ind_max_lq
      }
      else {
        c_bar_e = name_ind_max_lq
        newmat_e = newmat_e[match(name_ind_max_lq, rownames(newmat_e)), 
                            match(name_ind_max_lq, colnames(newmat_e))]
      }
      # cat("----------------------------------------------------", 
      #     "\n")
      # cat("Etap's ranking.", "\n")
      # cat("----------------------------------------------------", 
      #     "\n")
      # print(c_bar_e)
      # cat("----------------------------------------------------", 
      #     "\n")
      lambda_10 = lambda_1
      len_ind_max_lq == length(c_bar_e)
      etap = etap + 1
    }
    c_bar = c_bar_e
    new_mat = newmat_0[-match(c_bar_e, rownames(newmat_0)), 
                       match(c_bar_e, colnames(newmat_0))]
    to_rank = rownames(newmat)
    return(list(newmat = newmat, to_rank = to_rank, c_bar = c_bar))
  }
  compte <- function(symbole, seq) {
    seqbinaire <- rep(0, length(seq))
    seqbinaire[seq == symbole] <- 1
    nb <- sum(seqbinaire)
    return(nb)
  }
  mc1 = 0
  mc2 = 0
  md1 = 0
  md2 = 0
  mmv <- minmaxcriteria
  p_2 = PreferenceThresholds
  q_2 = IndifferenceThresholds
  v_2 = VetoThresholds
  m_def = mode_def
  pm = performanceMatrix
  cr <- criteria
  al = alternatives
  vp = criteriaWeights
  n = nrow(pm)
  mc <- matrix(rep(0, n * n), n, n)
  p_1 = c(rep(0, times = n))
  q_1 = c(rep(0, times = n))
  v_1 = c(rep(0, times = n))
  asc_ranking <- data.frame(Action = character(1), Rank = integer(1), 
                            stringsAsFactors = FALSE)
  dsc_ranking <- data.frame(Action = character(1), Rank = integer(1), 
                            stringsAsFactors = FALSE)
  
  
  ranking = list()
  mc = diag(1, n)
  md = diag(0, n)
  # print(m_def)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(mmv)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(p_1)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(p_2)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(q_1)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(q_2)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(v_1)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(v_2)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  for (j in 1:ncol(pm)) {
    if ((m_def[j] == "D") && (mmv[j] == "max")) {
      if (p_1[j] < (-1)) {
        stop(" alpha_p is less than -1 ")
      }
      if (q_1[j] < (-1)) {
        stop(" alpha_q is less than -1 ")
      }
      if (!(is.na(v_1[j]))) {
        if (v_1[j] < (-1)) {
          stop(" retourne NA")
        }
      }
    }
    if ((m_def[j] == "I") && (mmv[j] == "min")) {
      if (p_1[j] < -1) {
        stop(" alpha_p is less than -1 ")
      }
      if (q_1[j] < -1) {
        stop(" Please check the limits or bounds of the thresholds")
      }
      if (!(is.na(v_1[j]))) {
        if (v_1[j] < (-1)) {
          cat("v_1 is less than (-1)", "\n")
          stop(" Please check the limits or bounds of the thresholds")
        }
      }
    }
    if ((m_def[j] == "D") && (mmv[j] == "min")) {
      if (p_1[j] > 1) {
      }
      if (q_1[j] > 1) {
      }
      if (!(is.na(v_1[j]))) {
      }
      if (is.na((v_1[j] < -1))) {
      }
    }
    if ((m_def[j] == "I") && (mmv[j] == "max")) {
      if (p_1[j] > 1) {
      }
      if (q_1[j] > 1) {
      }
      if (!(is.na(v_1[j]))) {
      }
      if (is.na((v_1[j] < -1))) {
      }
    }
  }
  if (!(is.na(match("I", m_def)))) {
    for (j in 1:ncol(pm)) {
      if (m_def[j] == "I") {
        alpha_p = p_1[j]
        alpha_q = q_1[j]
        alpha_v = v_1[j]
        if (mmv[j] == "min") {
          p_1[j] = p_1[j]/(1 + alpha_p)
          p_2[j] = p_2[j]/(1 + alpha_p)
          q_1[j] = q_1[j]/(1 + alpha_q)
          q_2[j] = q_2[j]/(1 + alpha_q)
          v_1[j] = v_1[j]/(1 + alpha_v)
          v_2[j] = v_2[j]/(1 + alpha_v)
        }
        else {
          if (mmv[j] == "max") {
            p_1[j] = p_1[j]/(1 - alpha_p)
            p_2[j] = p_2[j]/(1 - alpha_p)
            q_1[j] = q_1[j]/(1 - alpha_q)
            q_2[j] = q_2[j]/(1 - alpha_q)
            v_1[j] = v_1[j]/(1 - alpha_v)
            v_2[j] = v_2[j]/(1 - alpha_v)
          }
        }
      }
    }
  }
  
  mc1 = 0
  mc2 = 0
  for (i in 1:nrow(pm)) {
    k = i + 1
    while (k <= n) {
      for (j in 1:ncol(pm)) {
        if ((mmv[j] == "max") && (m_def[j] == "D")) {
          c_ik = ((p_1[j] * pm[i, j] + p_2[j]) + pm[i, 
                                                    j] - pm[k, j])/((p_1[j] * pm[i, j] + p_2[j]) - 
                                                                      (q_1[j] * pm[i, j] + q_2[j]))
          c_ki = ((p_1[j] * pm[k, j] + p_2[j]) + pm[k, 
                                                    j] - pm[i, j])/((p_1[j] * pm[k, j] + p_2[j]) - 
                                                                      (q_1[j] * pm[k, j] + q_2[j]))
        }
        if ((mmv[j] == "min") && (m_def[j] == "D")) {
          c_ik = ((p_1[j] * pm[i, j] + p_2[j]) - (pm[i, 
                                                     j] - pm[k, j]))/((p_1[j] * pm[i, j] + p_2[j]) - 
                                                                        (q_1[j] * pm[i, j] + q_2[j]))
          c_ki = ((p_1[j] * pm[k, j] + p_2[j]) - (pm[k, 
                                                     j] - pm[i, j]))/((p_1[j] * pm[k, j] + p_2[j]) - 
                                                                        (q_1[j] * pm[k, j] + q_2[j]))
        }
        if ((mmv[j] == "max") && (m_def[j] == "I")) {
          c_ik = ((p_1[j] * pm[i, j] + p_2[j]) + pm[i, 
                                                    j] - pm[k, j])/((p_1[j] * pm[i, j] + p_2[j]) - 
                                                                      (q_1[j] * pm[i, j] + q_2[j]))
          c_ki = ((p_1[j] * pm[k, j] + p_2[j]) + pm[k, 
                                                    j] - pm[i, j])/((p_1[j] * pm[k, j] + p_2[j]) - 
                                                                      (q_1[j] * pm[k, j] + q_2[j]))
        }
        if ((mmv[j] == "min") && (m_def[j] == "I")) {
          c_ik = ((p_1[j] * pm[i, j] + p_2[j]) - (pm[i, 
                                                     j] - pm[k, j]))/((p_1[j] * pm[i, j] + p_2[j]) - 
                                                                        (q_1[j] * pm[i, j] + q_2[j]))
          c_ki = ((p_1[j] * pm[k, j] + p_2[j]) - (pm[k, 
                                                     j] - pm[i, j]))/((p_1[j] * pm[k, j] + p_2[j]) - 
                                                                        (q_1[j] * pm[k, j] + q_2[j]))
        }
        if (c_ik <= 0) {
          c10 = 0
        }
        else if (c_ik >= 1) {
          c10 = 1
        }
        else {
          c10 = c_ik
        }
        if (c_ki <= 0) {
          c20 = 0
        }
        else if (c_ki >= 1) {
          c20 = 1
        }
        else {
          c20 = c_ki
        }
        mc1 = round(mc1 + c10 * vp[j], digits = 4)
        mc2 = round(mc2 + c20 * vp[j], digits = 4)
      }
      mc[i, k] = round(mc1/sum(vp), digits = 4)
      mc[k, i] = round(mc2/sum(vp), digits = 4)
      mc1 = 0
      mc2 = 0
      k = k + 1
    }
  }
  col_d = matrix(c(rep(0, n * n)), nrow = n)
  for (i in 1:n) {
    for (j in 1:n) {
      col_d[i, j] = paste(i, "R", j, sep = "")
    }
  }
  name_d = as.vector(t(col_d))
  n = nrow(pm)
  m = ncol(pm)
  dv <- matrix(rep(0, n * n * m), n * n, m)
  l = 1
  for (i in 1:nrow(pm)) {
    k = 1
    while (k <= n) {
      for (j in 1:ncol(pm)) {
        if ((!(is.na(v_1[j]))) && !(is.na(v_2[j]))) {
          if ((mmv[j] == "max") && (m_def[j] == "D")) {
            d_ik = (pm[k, j] - pm[i, j] - (p_1[j] * 
                                             pm[i, j] + p_2[j]))/((v_1[j] * pm[i, j] + 
                                                                     v_2[j]) - (p_1[j] * pm[i, j] + p_2[j]))
          }
          if ((mmv[j] == "min") && (m_def[j] == "D")) {
            d_ik = ((pm[i, j] - (p_1[j] * pm[i, j] + 
                                   p_2[j]) - pm[k, j]))/((v_1[j] * pm[i, 
                                                                      j] + v_2[j]) - (p_1[j] * pm[i, j] + p_2[j]))
          }
          if ((mmv[j] == "max") && (m_def[j] == "I")) {
            d_ik = (pm[k, j] - pm[i, j] - (p_1[j] * 
                                             pm[i, j] + p_2[j]))/((v_1[j] * pm[i, j] + 
                                                                     v_2[j]) - (p_1[j] * pm[i, j] + p_2[j]))
          }
          if ((mmv[j] == "min") && (m_def[j] == "I")) {
            d_ik = ((pm[i, j] - (p_1[j] * pm[i, j] + 
                                   p_2[j]) - pm[k, j]))/((v_1[j] * pm[i, 
                                                                      j] + v_2[j]) - (p_1[j] * pm[i, j] + p_2[j]))
          }
        }
        else {
          d_ik = 0
        }
        if (d_ik <= 0) {
          d10 = 0
        }
        else if (d_ik >= 1) {
          d10 = 1
        }
        else {
          d10 = d_ik
        }
        dv[l, j] = round(d10, digits = 4)
      }
      l = l + 1
      k = k + 1
    }
  }
  v_mc = as.vector(t(mc))
  v_cred = c(rep(0, n * n))
  v_cum = 1
  m = ncol(pm)
  for (i in 1:(n * n)) {
    if (max(dv[i, ]) == 1) {
      v_cred[i] = 0
    }
    else if (max(dv[i, ]) < v_mc[i]) {
      v_cred[i] = v_mc[i]
    }
    else if (max(dv[i, ]) > v_mc[i]) {
      v_cum = 1
      for (j in 1:m) {
        if (dv[i, j] > v_mc[i]) {
          v_cum = v_cum * ((1 - dv[i, j])/(1 - v_mc[i]))
        }
      }
      v_cum = v_mc[i] * v_cum
      v_cred[i] = round(v_cum, digits = 4)
    }
  }
  dv = round(dv, digits = 4)
  mat_cred = round(matrix(v_cred, ncol = n, nrow = n), digits = 4)
  mat_cred = t(mat_cred)
  rownames(pm) = al
  colnames(pm) = cr
  rownames(mc) = al
  colnames(mc) = al
  rownames(mat_cred) = al
  colnames(mat_cred) = al
  rownames(dv) = name_d
  colnames(dv) = cr
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("Performance Matrix", "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(pm)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("Concordance Matrix", "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(mc)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("Criteria Discordance Table ", "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(dv)
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("Credibility Matrix", "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # print(mat_cred)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("---------------------------------------------------------    Ascending distillation     ----------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("-----------------------------------------------Beginning of the    Ascending distillation   ------------------------------------------", 
  #     "\n")
  # cat("--------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  to_rank_0 = al
  len = length(to_rank_0)
  c_bar = list()
  beta = 0.3
  alpha = 0.15
  compt_d = 1
  to_rank = to_rank_0
  newmat = mat_cred
  newmat_0 = mat_cred
  len_to_rank = length(al)
  len_to_rank_0 = length(al)
  r = 0
  while (len_to_rank_0 != 1 && nrow(newmat) > 1) {
    # cat(paste("Distillation_", compt_d, sep = ""), "\n")
    z = etape_asc(newmat, to_rank, c_bar, alpha, beta)
    c_bar = union(c_bar, z$c_bar)
    newmat = newmat_0[-match(c_bar, rownames(newmat_0)), 
                      -match(c_bar, colnames(newmat_0))]
    to_rank = z$to_rank
    len_to_rank_0 = len_to_rank - length(c_bar)
    ranking = union(ranking, c_bar)
    # cat("----------------------------------------------------------------------------------------", 
    #     "\n")
    zc_bar = z$c_bar
    c = length(zc_bar)
    j = 1
    for (i in (r + 1):(r + c)) {
      asc_ranking[i, 1] = zc_bar[j]
      asc_ranking[i, 2] = compt_d
      j = j + 1
    }
    r = nrow(asc_ranking)
    to_rank_0 = setdiff(to_rank_0, c_bar)
    if (len_to_rank_0 == 1) {
      asc_ranking[nrow(asc_ranking) + 1, 1] = to_rank_0
      asc_ranking[nrow(asc_ranking), 2] = compt_d + 1
    }
    if (len_to_rank_0 == 0) {
      len_to_rank_0 = 1
    }
    compt_d = compt_d + 1
  }
  b_e = max(asc_ranking[, 2]) + min(asc_ranking[, 2])
  for (i in 1:length(al)) {
    asc_ranking[i, 2] = b_e - asc_ranking[i, 2]
  }
  asc_ranking = asc_ranking[order(-asc_ranking[, 2]), ]
  # print(asc_ranking)
  # cat("------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("----------------------------------  End of the Ascending distillation    -----------------------------------", 
  #     "\n")
  # cat("------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  asc = asc_ranking
  # cat("-----------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("-------------------------Beginning of the    Descending distillation   ------------------------------------", 
  #     "\n")
  # cat("-----------------------------------------------------------------------------------------------------------", 
  #     "\n")
  to_rank_0 = al
  len = length(to_rank_0)
  c_bar = list()
  beta = 0.3
  alpha = 0.15
  compt_d = 1
  to_rank = to_rank_0
  newmat = mat_cred
  newmat_0 = mat_cred
  len_to_rank = length(al)
  len_to_rank_0 = length(al)
  r = 0
  while (len_to_rank_0 != 1 && nrow(newmat) > 1) {
    # cat(paste("Distillation_", compt_d, sep = ""), "\n")
    z = etape_dsc(newmat, to_rank, c_bar, alpha, beta)
    c_bar = union(c_bar, z$c_bar)
    newmat = newmat_0[-match(c_bar, rownames(newmat_0)), 
                      -match(c_bar, colnames(newmat_0))]
    to_rank = z$to_rank
    len_to_rank_0 = len_to_rank - length(c_bar)
    ranking = union(ranking, c_bar)
    # cat("-------------------------------------------------------------------------------------------", 
    #     "\n")
    zc_bar = z$c_bar
    c = length(zc_bar)
    j = 1
    for (i in (r + 1):(r + c)) {
      dsc_ranking[i, 1] = zc_bar[j]
      dsc_ranking[i, 2] = compt_d
      j = j + 1
    }
    r = nrow(dsc_ranking)
    to_rank_0 = setdiff(to_rank_0, c_bar)
    # cat("-----------------------------------------------------------------------------------------", 
    #     "\n")
    if (len_to_rank_0 == 1) {
      dsc_ranking[nrow(dsc_ranking) + 1, 1] = to_rank_0
      dsc_ranking[nrow(dsc_ranking), 2] = compt_d + 1
    }
    if (len_to_rank_0 == 0) {
      len_to_rank_0 = 1
    }
    compt_d = compt_d + 1
  }
  dsc = dsc_ranking[order(dsc_ranking[, 2], dsc_ranking[, 
                                                        1]), ]
  # cat("--------------------------------  End of the Descending distillation   ---------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("--------------------------------  Ascending distillation ranking  ---------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(asc_ranking)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("--------------------------------  Descending distillation ranking  ---------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(dsc_ranking)
  # cat(" ", "\n")
  # cat(" ", "\n")
  n = nrow(pm)
  matranking <- matrix(rep(0, n * n), n, n)
  mrank <- matrix(rep(0, n * n), n, n)
  d_matrank = c(rep("I", times = n))
  diag(matranking) = d_matrank
  al = dsc[, 1]
  rownames(matranking) = al
  colnames(matranking) = al
  rownames(mrank) = al
  colnames(mrank) = al
  final_ranking <- data.frame(alternative = al, sum_outrank = c(rep(0, 
                                                                    times = length(al))), ranking = c(rep(0, times = length(al))), 
                              stringsAsFactors = FALSE)
  # print(al)
  for (i in 1:n) {
    for (j in 1:n) {
      if ((dsc[which(dsc$Action == al[i]), 2] < dsc[which(dsc$Action == 
                                                          al[j]), 2]) && (asc[which(asc$Action == al[i]), 
                                                                              2] <= asc[which(asc$Action == al[j]), 2])) {
        matranking[al[i], al[j]] = "P"
        mrank[al[i], al[j]] = 1
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] <= 
                dsc[which(dsc$Action == al[j]), 2]) && (asc[which(asc$Action == 
                                                                  al[i]), 2] < asc[which(asc$Action == al[j]), 
                                                                                   2])) {
        matranking[al[i], al[j]] = "P"
        mrank[al[i], al[j]] = 1
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] > dsc[which(dsc$Action == 
                                                               al[j]), 2]) && (asc[which(asc$Action == al[i]), 
                                                                                   2] >= asc[which(asc$Action == al[j]), 2])) {
        matranking[al[i], al[j]] = "NP"
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] >= 
                dsc[which(dsc$Action == al[j]), 2]) && (asc[which(asc$Action == 
                                                                  al[i]), 2] > asc[which(asc$Action == al[j]), 
                                                                                   2])) {
        matranking[al[i], al[j]] = "NP"
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] == 
                dsc[which(dsc$Action == al[j]), 2]) && (asc[which(asc$Action == 
                                                                  al[i]), 2] == asc[which(asc$Action == al[j]), 
                                                                                    2])) {
        matranking[al[i], al[j]] = "I"
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] < dsc[which(dsc$Action == 
                                                               al[j]), 2]) && (asc[which(asc$Action == al[i]), 
                                                                                   2] > asc[which(asc$Action == al[j]), 2])) {
        matranking[al[i], al[j]] = "R"
        mrank[al[i], al[j]] = 1
      }
      else if ((dsc[which(dsc$Action == al[i]), 2] > dsc[which(dsc$Action == 
                                                               al[j]), 2]) && (asc[which(asc$Action == al[i]), 
                                                                                   2] < asc[which(asc$Action == al[j]), 2])) {
        matranking[al[i], al[j]] = "R"
        mrank[al[i], al[j]] = 1
      }
    }
  }
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------  Final Ranking Matrix    -----------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(matranking)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ---------------------------    End of Final Ranking Matrix    ----------------------------------", 
  #     "\n")
  for (i in 1:n) {
    seq = matranking[final_ranking[i, 1], ]
    final_ranking[i, 2] = compte("P", seq)
  }
  final_ranking = final_ranking[order(-final_ranking[, 2], 
                                      final_ranking[, 1]), ]
  j = 1
  for (i in 1:n - 1) {
    if (matranking[final_ranking[i, 1], final_ranking[i + 
                                                      1, 1]] == "P" && i == 1) {
      final_ranking[i, 3] = j
      final_ranking[i + 1, 3] = j + 1
      j = j + 1
    }
    if (matranking[final_ranking[i, 1], final_ranking[i + 
                                                      1, 1]] == "I" && i == 1) {
      final_ranking[i, 3] = i
      final_ranking[i + 1, 3] = i
      j = j + 1
    }
    else if (i > 1) {
      if ((matranking[final_ranking[i, 1], final_ranking[i + 
                                                         1, 1]] == "P") && (final_ranking[i, 2] > 1)) {
        final_ranking[i, 3] = j
        final_ranking[i + 1, 3] = j + 1
        j = j + 1
      }
      else if ((matranking[final_ranking[i, 1], final_ranking[i + 
                                                              1, 1]] == "P") && (final_ranking[i + 1, 2] == 
                                                                                 0)) {
        final_ranking[i, 3] = j
        final_ranking[i + 1, 3] = j + 1
        j = j + 1
      }
      else if ((matranking[final_ranking[i, 1], final_ranking[i + 
                                                              1, 1]] == "R") && (final_ranking[i + 1, 2] == 
                                                                                 0)) {
        final_ranking[i, 3] = j
        final_ranking[i + 1, 3] = final_ranking[i, 3] + 
          1
      }
      else if ((matranking[final_ranking[i, 1], final_ranking[i + 
                                                              1, 1]] == "I") && (final_ranking[i + 1, 2] == 
                                                                                 0)) {
        final_ranking[i + 1, 3] = final_ranking[i, 3]
      }
      else if (matranking[final_ranking[i, 1], final_ranking[i + 
                                                             1, 1]] == "I" && (final_ranking[i + 1, 2] != 
                                                                               0)) {
        final_ranking[i + 1, 3] = final_ranking[i, 3]
      }
      else if (matranking[final_ranking[i, 1], final_ranking[i + 
                                                             1, 1]] == "R" && (final_ranking[i + 1, 2] != 
                                                                               0)) {
        final_ranking[i + 1, 3] = final_ranking[i, 3]
      }
    }
  }
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(final_ranking[, -2])
  names_matrank_adj = final_ranking[, 1]
  matrank_adj <- matrix(rep(0, n * n), n, n)
  rownames(matrank_adj) = names_matrank_adj
  colnames(matrank_adj) = names_matrank_adj
  for (i in 1:n) {
    for (j in 1:n) {
      if ((final_ranking[j, 3] - final_ranking[i, 3] == 
           1) && (matranking[final_ranking[i, 1], final_ranking[j, 
                                                                1]] == "P")) {
        matrank_adj[i, j] = 1
      }
      if ((final_ranking[j, 3] - final_ranking[i, 3] == 
           1) && (matranking[final_ranking[i, 1], final_ranking[j, 
                                                                1]] == "I")) {
        matrank_adj[i, j] = 1
      }
      if ((final_ranking[j, 3] - final_ranking[i, 3] == 
           1) && (matranking[final_ranking[i, 1], final_ranking[j, 
                                                                1]] == "R")) {
        matrank_adj[i, j] = 1
      }
    }
  }
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("------------------------------------------  adjacent  Ranking Matrix    -------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(matrank_adj)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  #g1 <- graph.adjacency(matrank_adj)
  #g2 = plot(g1)
  final_ranking = final_ranking[, -2]
  #sink("result.txt")
  # cat("------------------------------------------------------------------------------  Performance table    --------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(pm)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Concordance  matrix    -------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(mc)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Discordance  table    --------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(dv)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Credibility matrix -----------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(mat_cred)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Ascending ranking   ----------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(asc_ranking)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Descending ranking   ---------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(dsc_ranking)
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-----------------------------------------------------------------------------  Final ranking  ---------------------------------------------------------------------------------", 
  #     "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # print(final_ranking) # FINAL MATRIX
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # sink()
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat(" ", "\n")
  # cat("----------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  # cat("End of the calculation", "\n")
  # cat("----------------------------------------------------------------------------------------------------------------", 
  #     "\n")
  print("RESULT_OK")
  out <- list(`Performance Matrix` = pm, `Concordance Matrix` = mc, 
              `Criteria Discordance Table` = dv, `Credibility Matrix` = mat_cred, 
              `Ascending distillation ranking` = asc_ranking, `Descending distillation ranking` = dsc_ranking, 
              `Final Ranking Matrix` = final_ranking)
  return(out)
}



args = commandArgs(trailingOnly=TRUE)

## T
#args[1]= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/data"
#args[2]= "/data2"
#args[3] = "2,1" #criteriaWeights
#args[4] = "1,10,3" #IndifferenceThresholds 
#args[5] = "1,10,3" #PreferenceThresholds 
#args[6] = "NA,NA,NA" #vetos
#args[7] = "min,max" #criteriaMinMax



pathIN <- paste(args[1],args[2],".csv",sep="")
pathOUT <- paste(args[1],args[2],"_r.csv",sep="")

colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
performanceMatrix <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)
#performanceMatrix <- read.table(file=pathIN, header=F, sep=",")
alternatives <- rownames(performanceMatrix)
criteria <- colnames(performanceMatrix)

criteriaWeights <- as.numeric(unlist(strsplit(args[3], ",")))
IndifferenceThresholds <- as.numeric(unlist(strsplit(args[4], ",")))
PreferenceThresholds <- as.numeric(unlist(strsplit(args[5], ",")))
VetoThresholds <- as.numeric(unlist(strsplit(args[6], ",")))
minmaxcriteria <- c(unlist(strsplit(args[7], ",")))

#print(performanceMatrix)
#print(alternatives)
print(criteria)
print(IndifferenceThresholds)
print(PreferenceThresholds)
print(VetoThresholds)
print(minmaxcriteria)

out <- Electre3_SimpleThresholds(performanceMatrix,
  alternatives,
  criteria,
  minmaxcriteria,
  criteriaWeights,
  IndifferenceThresholds,
  PreferenceThresholds,
  VetoThresholds)

# print(out["Final Ranking Matrix"])
 # df <- out["Final Ranking Matrix"]
# print(pathOUT)

df <- data.frame(out['Final Ranking Matrix'])
print(df["Final.Ranking.Matrix.alternative"])

write.csv(out["Final Ranking Matrix"], file = pathOUT)
# write.csv(IndifferenceThresholds, file = pathOUT)
