# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 10:57:37 2019
SUDOKU SOLVER V12
-box line reduction added
@author: omerzulal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
import warnings
warnings.filterwarnings("ignore")
import time
         
            
#%% validation check functions
def row_check(board,isprint=False):
    check = True
    for row in range(9):
        a = board.iloc[row,:].value_counts()
        check = check and not any(a[a.index != "."]>1)
     
    if isprint:
        if check:
            print("Row Check: Passed")
        else:
            print("Row Check: Failed")
        
    return check

def col_check(board,isprint=False):
    check = True
    for col in range(9):
        a = board.iloc[:,col].value_counts()
        check = check and not any(a[a.index != "."]>1)
    
    if isprint:
        if check:
            print("Column Check: Passed")
        else:
            print("Column Check: Failed")
        
    return check

def square_check(board,isprint=False):
    check = True
    for i in [[0,1,2],[3,4,5],[6,7,8]]:
        for j in [[0,1,2],[3,4,5],[6,7,8]]:
            a = pd.Series(board.iloc[i,j].values.flatten()).value_counts()
            check = check and not any(a[a.index != "."]>1)
    if isprint:     
        if check:
            print("Square Check: Passed")
        else:
            print("Square Check: Failed")
        
    return check

def check_valid():
    rcheck = row_check(board)
    ccheck = col_check(board)
    cucheck = square_check(board)
    
    return rcheck and ccheck and cucheck

#%% PRINT THE SUDOKU BOARD
#print the board
def print_board(board):
    boardprint = board.copy()
    boardprint.columns = range(1,10)
    boardprint.index = ["A","B","C","D","E","F","G","H","I"]
    # sns.heatmap(board,annot=True,linecolor="k")
    print(boardprint)
    
#%% INITIALISE CANDIDATES
def candidates(board):
    # board_copy = board.copy()
    cands = pd.DataFrame(np.full((9,9),np.nan))
    for row in range(9):
        for col in range(9):
            temp = []
            if board.iloc[row,col] == ".":
                temp.extend(board.iloc[row,:])
                temp.extend(board.iloc[:,col])
                temp.extend(board.loc[board.index[row]][board.columns[col]].values.flatten())
                temp = pd.Series(temp)
                drops = temp[temp!="."].unique()
                cand = pd.Series(np.arange(1,10),index=np.arange(1,10)).drop(drops).values.astype("O")
                
                #this part is for handling the "ValueError: setting an array element as a sequence"
                if len(cand) == 1:
                    if cand%1 == 0.0:
                        temp = cand.tolist()
                        temp.append(99)
                        cands[col][row] = np.array(temp).astype("O")
                        temp.remove(99)
                        cands[col][row] = np.array(temp).astype("O")
                else:
                    cands[col][row] = cand

    return cands

### Original version
# def candidates(board):
#     cands = pd.DataFrame(np.full((9,9),np.nan))
#     for row in range(9):
#         for col in range(9):
#             temp = []
#             if board.iloc[row,col] == ".":
#                 temp.extend(board.iloc[row,:])
#                 temp.extend(board.iloc[:,col])
#                 temp.extend(board.loc[board.index[row]][board.columns[col]].values.flatten())
#                 temp = pd.Series(temp)
#                 drops = temp[temp!="."].unique()
#                 cand = pd.Series(np.arange(1,10),index=np.arange(1,10)).drop(drops).values.astype("O")
#                 cands[col][row] = cand
#     return cands

#%% UPDATE CANDIDATES
def candidates_update(cands,row,col,val):
    cands.loc[row][col] = np.nan
    # val = int(val)
    
    #remove from rows
    temp1 = cands.loc[row].dropna().apply(lambda x: val in x)
    inx = temp1.index[temp1 == True]
    if len(inx):
        for i in inx:
            try:
                temp = cands.loc[row][i].tolist()
            except:
                temp = cands.loc[row][i]
            temp.remove(val)
            cands.loc[row][i] = np.array(temp)
    
    #remove from columns
    temp1 = cands[col].dropna().apply(lambda x: val in x)
    inx = temp1.index[temp1 == True]
    if len(inx):
        for i in inx:
            try:
                temp = cands[col][i].tolist()
            except:
                temp = cands[col][i]
            
            temp.remove(val)
            cands[col][i] = np.array(temp)
    
    #remove from squares
    temp = pd.Series([[0,1,2],[3,4,5],[6,7,8]])
    rowx = temp[[row in i for i in temp]].tolist()[0]
    colx = temp[[col in i for i in temp]].tolist()[0]
    a = cands.iloc[rowx,colx]
    
    for ii in a.index:
        for jj in a.columns:
            try:
                temp1 = a.loc[ii][jj].tolist()
                temp1.remove(val)
                a.loc[ii][jj] = np.array(temp1)
            except:
                pass
    cands.iloc[rowx,colx] = np.array(a)
    return cands

#%% SINGLE CANDIDATES
def single_cand(board,cands):
    ischanged = 0
    for row in range(9):
        for col in range(9):
            if board.iloc[row,col] == ".":
                cand = cands.iloc[row,col]
                # cand = int(cands.iloc[row,col][0])
                try:
                    lenx = len(cand)
                    if lenx == 1:
                        ischanged = 1
                        print(f"R{row+1}C{col+1}={cand[0]} : Single Candidate")
                        board.iloc[row,col] = cand[0]
                        cands = candidates_update(cands,row,col,cand[0])
                except:
                    ischanged = 1
                    print(f"R{row+1}C{col+1}={cand} : Single Candidate (except)")
                    board.iloc[row,col] = cand
                    cands = candidates_update(cands,row,col,cand)
    if ischanged:
        board,cands = solver(board,cands)               
    return board,cands

#%% HIDDEN SINGLES
def hidden_singles(board,cands):
    ischanged = 0
    #check rows
    for row in range(9):
        temp = []
        for col in range(9):
            if board.iloc[row,col] == ".":
                temp.extend(cands.iloc[row,col])
        valco = pd.Series(temp).value_counts()
        for valun in valco.index[valco == 1].values: #????? there can be 1 and only 1 single candidate in a row..
            temp1 = cands.loc[row].dropna().apply(lambda x: valun in x)
            inx = temp1.index[temp1 == True]
            if len(inx):
                ischanged = 1
                for inxt in inx:
                    print(f"R{row+1}C{inxt+1}={valun} : Hidden Singles (row)")
                    board.iloc[row,inxt] = valun
                    cands = candidates_update(cands,row,inxt,valun)
    
    #check columns
    for col in range(9):
        temp = []
        for row in range(9):
            if board.iloc[row,col] == ".":
                temp.extend(cands.iloc[row,col])
        valco = pd.Series(temp).value_counts()
        for valun in valco.index[valco == 1].values:
            temp1 = cands.iloc[:,col].dropna().apply(lambda x: valun in x)
            inx = temp1.index[temp1 == True]
            if len(inx):
                ischanged = 1
                for inxt in inx:
                    print(f"R{inxt+1}C{col+1}={valun} : Hidden Singles (col)")
                    board.iloc[inxt,col] = valun
                    cands = candidates_update(cands,inxt,col,valun)        

    #check squares
    for i in [[0,1,2],[3,4,5],[6,7,8]]:
        for j in [[0,1,2],[3,4,5],[6,7,8]]:
            a = cands.iloc[i,j]
            a_flat = pd.Series(a.values.flatten()).dropna()
            temp = []
            for ix in a_flat: 
                temp.extend(ix)
            valco = pd.Series(temp).value_counts()
            
            if any(valco == 1):
                to_change_all = valco.index[valco == 1].values
                for to_change in to_change_all: #loop all values to be changed (sometimes multiple changes needed in a single box)
                    for rowx in a.index:
                        for colx in a.columns:
                            try: 
                                if board.iloc[rowx,colx] == ".":
                                    if to_change in a.loc[rowx][colx]:
                                        print(f"R{rowx+1}C{colx+1}={to_change} : Hidden Singles (square)")
                                        board.iloc[rowx,colx] = to_change
                                        cands = candidates_update(cands,rowx,colx,to_change)
                                        ischanged = 1
                            except:
                                print("except")
    if ischanged:
        board,cands = solver(board,cands)                       
    return board,cands

#%% HIDDEN PAIRS
def hidden_pairs(board,cands):
    ischanged = 0

    # ROWS
    # construct candidate table for rows
    cand_inxs = []
    for i in range(1,10):
        candx = []
        for rows in cands.index:
            use = cands.loc[rows].dropna()
            temp = []
            for cols in use.index:
                if i in use[cols]:
                    temp.append(cols)
            candx.append(temp)
        cand_inxs.append(candx) 
    
    # loop through rows to find hidden pairs
    for rows in range(9): #loop rows of candidates
    # for rows in [7]: #loop rows of candidates
        omer = {}
        for candx in range(9): #loop candidates from 1 to 9
            # print(f"number = {candx+1}, found in cols {cand_inxs[candx][rows]}")
            omer[candx+1] = cand_inxs[candx][rows]
            
        omer = pd.Series(omer)        
        omer = omer[omer.apply(lambda x: len(x)>0)]
        valco = omer.value_counts()  
        
        try:
            cols_to_remove = valco[valco==2].index.tolist()[0]
            if len(cols_to_remove) == 2:
                vals_to_remove = omer.index[omer.apply(lambda x: x != cols_to_remove)].values
                temp = cands.loc[rows][cols_to_remove]
                
                for col in temp.index:
                    temp1 = temp[col].tolist()
                    for rem in vals_to_remove:
                        try:
                            temp1.remove(rem)
                            print(f"R{rows}C{col}     Hidden Pairs (row), {rem} removed")
                            ischanged = 1
                        except:
                            pass
        
                    temp[col] = np.array(temp1)
                
                cands.loc[rows][cols_to_remove] = temp
        except:
            pass
    
    # COLUMNS
    cand_inxs = []
    for i in range(1,10):
        candx = []
        for cols in cands.columns:
            use = cands[cols].dropna()
            temp = []
            for rows in use.index:
                if i in use.loc[rows]:
                    temp.append(rows)
            candx.append(temp)
        cand_inxs.append(candx) 
    
    # loop through cols to find hidden pairs
    for cols in range(9): #loop cols of candidates
        omer = {}
        for candx in range(9): #loop candidates from 1 to 9
            omer[candx+1] = cand_inxs[candx][cols]
            
        omer = pd.Series(omer)        
        omer = omer[omer.apply(lambda x: len(x)>0)]
        valco = omer.value_counts()  
        
        try:
            rows_to_remove = valco[valco==2].index.tolist()[0]
            if len(rows_to_remove) == 2:
                vals_to_remove = omer.index[omer.apply(lambda x: x != rows_to_remove)].values
                temp = cands[cols][rows_to_remove]
                
                for row in temp.index:
                    temp1 = temp.loc[row].tolist()
                    for rem in vals_to_remove:
                        try:
                            temp1.remove(rem)
                            print(f"R{row}C{cols}     Hidden Pairs (col), {rem} removed")
                            ischanged = 1
                        except:
                            pass
        
                    temp.loc[row] = np.array(temp1)
                
                cands[cols][rows_to_remove] = temp
        except:
            pass
        
    #BOX
    for i in [[0,1,2],[3,4,5],[6,7,8]]:
        for j in [[0,1,2],[3,4,5],[6,7,8]]:
            use = cands.iloc[i,j]    
            use_flat = pd.Series(use.values.flatten()).dropna()
            temp = []
            for ix in use_flat:
                temp.extend(ix)
            valco = pd.Series(temp).value_counts()
            valco_inx = valco.index[valco == 2]
            
            omer = {}
            for valun in valco_inx:
                tempinx = []
                for rows in use.index:
                    for cols in use.columns:
                        try:
                            if valun in use.loc[rows][cols]:
                                tempinx.append([rows,cols])
                        except:
                            pass
                omer[valun] = tempinx
            
            
            #find pairs
            omer = pd.Series(omer)
            omer.sort_index(inplace=True)
            
            pairs = []
            rowcol = []
            for pair1 in omer.index:
                for pair2 in omer.index[omer.index>pair1]:
                    if omer[pair1] == omer[pair2]:
                        pairs.append([pair1,pair2])
                        rowcol.append(omer[pair1])
            
            if len(pairs):     
                #locate them in the box
                for pairvals,pairinx in zip(pairs,rowcol):
                    for inx in pairinx:
                        if cands.iloc[inx[0],inx[1]].tolist() == pairvals:
                            break
                        cands.iloc[inx[0],inx[1]] = np.array(pairvals)
                        ischanged = 1
                        print(f"R{inx[0]}C{inx[1]}     Hidden Pairs (square) {pairvals}")

    if ischanged:
        board,cands = solver(board,cands)
        
    return board,cands  

#%% HIDDEN TRIPLES (squares is missing)
    
def hidden_triples(board,cands):
    ischanged = 0
    
    # ROWS
    for rows in range(9):
        use = cands.loc[rows].dropna()
        vals = []
        for ix in use:
            vals.extend(ix)
        vals = pd.Series(vals).unique()
        #go through combinations (3 elements at a time)
        for comb in itertools.combinations(vals, 3):
            inxs = (use.apply(lambda x: comb[0] in x)) | (use.apply(lambda x: comb[1] in x)) | (use.apply(lambda x: comb[2] in x))
            if sum(inxs) == 3:
                #determine hidden triple indexes
                triple_inx = inxs.index[inxs]
                
                #remove values other than the triple
                for colx in triple_inx: #go through column indexes
                    temp = cands.loc[rows][colx].tolist()
                    val_to_remove = set(comb).symmetric_difference(temp)
                    for rem in val_to_remove:
                        try:
                            temp.remove(rem)
                            print(f"R{rows}C{colx}     Hidden Triple (rows), {rem} removed, Triple: {comb}")
                            ischanged = 1
                        except:
                            pass
                    cands.loc[rows][colx] = np.array(temp)
                    
    # COLUMNS
    for col in range(9):
        use = cands[col].dropna()
        vals = []
        for ix in use:
            vals.extend(ix)
        vals = pd.Series(vals).unique()
        #go through combinations (3 elements at a time)
        for comb in itertools.combinations(vals, 3):
            inxs = (use.apply(lambda x: comb[0] in x)) | (use.apply(lambda x: comb[1] in x)) | (use.apply(lambda x: comb[2] in x))
            if sum(inxs) == 3:
                #determine hidden triple indexes
                triple_inx = inxs.index[inxs]
                
                #remove values other than the triple
                for rowx in triple_inx:
                    temp = cands[col][rowx].tolist()
                    val_to_remove = set(comb).symmetric_difference(temp)
                    for rem in val_to_remove:
                        try:
                            temp.remove(rem)
                            print(f"R{rowx}C{col}     Hidden Triple (cols), {rem} removed, Triple: {comb}")
                            ischanged = 1
                        except:
                            pass
                    cands[col][rowx] = np.array(temp)

    if ischanged:
        board,cands = solver(board,cands)    
    return board,cands 

#%% NAKED PAIRS
def naked_pairs(board,cands):
    ischanged = 0
    
    #check rows
    for row in range(9):
        use = cands.loc[row].dropna()
        try:
            pairs = use[use.index[use.apply(lambda x: len(x) == 2)]]
            if len(pairs) >= 2:
                for i in pairs.index:
                    for j in pairs.index[pairs.index > i]:
                        if all(pairs[i] == pairs[j]):
                            # print(f"Row{row} Naked Pair: {pairs[i]}")
                            #remove found pair values in the rest of the cells in candidates
                            inxs = use.index.tolist()
                            inxs.remove(i)
                            inxs.remove(j)
                            for k in inxs:
                                temp = cands.loc[row][k].tolist()
                                for l in pairs[i]:
                                    try:
                                        temp.remove(l)
                                        print(f"R{row}C{k}     Naked Pair (row), {l} removed {pairs[i]}")
                                        ischanged = 1
                                    except:
                                        pass
                                        # print("No length item")
                                cands.loc[row][k] = np.array(temp)
        except:
            pass
            # print(f"No pair found in row")
            
    #check columns
    for col in range(9):
        use = cands[col].dropna()
        try:
            pairs = use[use.index[use.apply(lambda x: len(x) == 2)]]
            if len(pairs) >= 2:
                for i in pairs.index:
                    for j in pairs.index[pairs.index > i]:
                        if all(pairs[i] == pairs[j]):
                            #remove found pair values in the rest of the cells in candidates
                            inxs = use.index.tolist()
                            inxs.remove(i)
                            inxs.remove(j)
                            for k in inxs:
                                temp = cands[col][k].tolist()
                                for l in pairs[i]:
                                    try:
                                        temp.remove(l)
                                        print(f"R{k}C{col}     Naked Pair (col), {l} removed {pairs[i]}")
                                        ischanged = 1
                                    except:
                                        pass
                                        
                                cands[col][k] = np.array(temp)
                                
        except:
            pass
    
    #check squares
    for i in [[0,1,2],[3,4,5],[6,7,8]]:
        for j in [[0,1,2],[3,4,5],[6,7,8]]:
            use = cands.iloc[i,j]
            use_flat = pd.Series(use.values.flatten()).dropna()
            try:
                pairs = use_flat[use_flat.index[use_flat.apply(lambda x: len(x) == 2)]]
                if len(pairs) >= 2:
                    for pair1 in pairs.index:
                        for pair2 in pairs.index[pairs.index > pair1]:
                            if all(pairs[pair1] == pairs[pair2]):
                                # print(f"Square Naked Pair: {pairs[pair1]}")
                                #remove found pair values in the rest of the cells in candidates
                                
                                for ii in i:
                                    for jj in j:
                                        try:
                                            if len(use.loc[ii][jj])>=2:
                                                check = use.loc[ii][jj] == pairs[pair1]
                                                try:
                                                    check = all(check)
                                                except:
                                                    pass
                                                if not check:
                                                    temp = use.loc[ii][jj].tolist()
                                                    for l in pairs[pair1]:
                                                        try:
                                                            temp.remove(l)
                                                            print(f"R{ii}C{jj}     Naked Pair (square), {l} removed {pairs[pair1]}")
                                                            ischanged = 1
                                                        except:
                                                            pass
                                                    use.loc[ii][jj] = np.array(temp)
                                                
                                        except:
                                            pass
                                cands.iloc[i,j] = use
            except:
                pass
                
            
        
    if ischanged:
        board,cands = solver(board,cands)
        
    return board,cands

#%% NAKED TRIPLES (squares missing)
import itertools

def naked_triples(board,cands):
    ischanged = 0
    
    #rows
    for row in range(9):
        use = cands.loc[row].dropna()
        
        #go through combinations (3 elements at a time)
        for comb in itertools.combinations(use, 3):
            comb = [i.tolist() for i in comb]
            temp = []
            for i in comb:
                temp.extend(i)
            naked_triple = pd.Series(temp).unique()
            if len(naked_triple) == 3:

                #remove naked triple elements from the rest of the row
                for j in use.index:
                    try:
                        used = use[j].tolist()
                        if not used in comb:
                            temp1 = used
                            for nt in naked_triple:
                                try:
                                    temp1.remove(nt)
                                    use[j] = np.array(temp1)
                                    print(f"R{row}C{j}     Naked Triple (rows), {nt} removed, Triple: {naked_triple}")
                                    ischanged = 1
                                except:
                                    pass
                    except:
                        pass
                        
                cands.loc[row] = use 

    #cols
    for col in range(9):
        use = cands[col].dropna()
        
        #go through combinations (3 elements at a time)
        for comb in itertools.combinations(use, 3):
            comb = [i.tolist() for i in comb]
            temp = []
            for i in comb:
                temp.extend(i)
            naked_triple = pd.Series(temp).unique()
            if len(naked_triple) == 3:

                #remove naked triple elements from the rest of the column
                for j in use.index:
                    try:
                        used = use[j].tolist()
                        if not used in comb:
                            temp1 = used
                            for nt in naked_triple:
                                try:
                                    temp1.remove(nt)
                                    use[j] = np.array(temp1)
                                    print(f"R{j}C{col}     Naked Triple (columns), {nt} removed, Triple: {naked_triple}")
                                    # print(f"Column{col} Naked triples removed {nt}, {comb}")
                                    ischanged = 1
                                except:
                                    pass
                    except:
                        pass
                        
                cands[col] = use 
                
    if ischanged:
        board,cands = solver(board,cands)
    return board,cands

#%% X-WING  
def x_wing(board,cands):
    #check xwings for both rows and columns
    for rowcol in ["rows","cols"]:
        if rowcol == "cols":
            cands = cands.T
        ischanged = 0
        #construct candidate table
        wings = []
        for i in range(1,10):
            wing = []
            for rows in cands.index:
                use = cands.loc[rows].dropna()
                temp = []
                for cols in use.index:
                    if i in use[cols]:
                        temp.append(cols)
                wing.append(temp)
            wings.append(wing)      
        
        #loop through the candidates and eliminate
        for wing in range(len(wings)):
            # print(wings[wing])
            for i in range(9):
                for j in range(i+1,9):
                    if (len(wings[wing][i]) == 2) & (len(wings[wing][j]) == 2):
                        # print(f"pair_r{i}c{j}")
                        if wings[wing][i] == wings[wing][j]:
                            #remove candidates in the columns
                            for rem in wings[wing][i]:
                                use = cands[rem].dropna()
                                for ix in use.index:
                                    if not((ix == i) | (ix == j)):
                                        temp = use[ix].tolist()
                                        try:
                                            temp.remove(wing+1)
                                            print(f"R{ix}C{rem}     X-Wing, removed {wing+1} from {rowcol}")
                                            ischanged = 1
                                        except:
                                            pass
                                        use[ix] = np.array(temp)
                                cands[rem] = use
    cands = cands.T
    if ischanged:
        board,cands = solver(board,cands)           
    return board,cands  

#%% POINTING PAIRS
def pointing_pairs(board,cands):
    ischanged = 0
    
    for i in [[0,1,2],[3,4,5],[6,7,8]]:
        for j in [[0,1,2],[3,4,5],[6,7,8]]:
            use = cands.iloc[i,j]
            use_flat = pd.Series(use.values.flatten()).dropna()
            
            temp = []
            for ix in use_flat:
                temp.extend(ix)
            
            valco = pd.Series(temp).value_counts()
            # try:
            pair_vals = valco.index[valco == 2]
            
            for pair_val in pair_vals:
                pointrows, pointcols = [],[]
                for ii in use.index:
                    for jj in use.columns:
                        try:
                            if pair_val in use.loc[ii][jj].tolist():
                                pointrows.extend([ii])
                                pointcols.extend([jj])
                        except:
                            pass
                        
                #pairs point in the column direction
                try:
                    if not np.diff(pointcols)[0]:
                        change_col = cands[pointcols[0]].dropna().drop(pointrows)
                        for rows in change_col.index:
                            temp = change_col[rows].tolist()
                            try:
                                temp.remove(pair_val)
                                cands.iloc[rows,pointcols[0]] = np.array(temp)
                                print(f"R{rows}C{pointcols[0]}     Pointing Pairs (cols), {pair_val} removed")
                                ischanged = 1
                            except:
                                pass
                except:
                    pass
                    
                #pairs point in the row direction
                try:
                    if not np.diff(pointrows)[0]:
                        change_col = cands.loc[pointrows[0]].dropna().drop(pointcols)
                        for cols in change_col.index:
                            temp = change_col[cols].tolist()
                            try:
                                temp.remove(pair_val)
                                cands.iloc[pointrows[0],cols] = np.array(temp)
                                print(f"R{pointrows[0]}C{cols}     Pointing Pairs (rows), {pair_val} removed")
                                ischanged = 1
                            except:
                                pass
                except:
                    pass
                    
    if ischanged:
        board,cands = solver(board,cands)  

    return board,cands

#%% BOX/LINE REDUCTION

def box_line(board,cands):
    ischanged = 0
    
    #rows
    for rows in range(9):
        use = cands.loc[rows].dropna()
        for val in range(1,10):
            inxs = use.apply(lambda x: val in x)
            if len(inxs) == 0:
                break
            inxs = list(inxs.index[inxs])
            
            #find locations of the box/line reduction candidates
            if len(inxs) == 2 or len(inxs) == 3:
                board_pos = square_pos.loc[rows][inxs]
                if np.diff(board_pos).sum() == 0:
                    square = board_pos.iloc[0]
                    inx = pd.Series(square_pos[square_pos == square].stack().index.tolist())
                    
                    #go through the square cells except the box/line
                    for ix in inx:
                        if ix[0] != rows:
                        # if ix != (rows,board_pos.index[0]) and ix != (rows,board_pos.index[1]) and ix != (rows,board_pos.index[2]):
                            try:
                                temp = cands.iloc[ix].tolist()
                                temp.remove(val)
                                cands.iloc[ix] = np.array(temp)
                                ischanged = 1
                                print(f"R{ix[0]}C{ix[1]}     Box/Line (row) reduction value {val} removed")
                            except:
                                pass
        
        #columns
        for cols in range(9):
            use = cands[cols].dropna()
            for val in range(1,10):
                inxs = use.apply(lambda x: val in x)
                if len(inxs) == 0:
                    break
                inxs = list(inxs.index[inxs])
                
                #find locations of the box/line reduction candidates
                if len(inxs) == 2 or len(inxs) == 3:
                    board_pos = square_pos[cols][inxs]
                    if np.diff(board_pos).sum() == 0:
                        square = board_pos.iloc[0]
                        inx = pd.Series(square_pos[square_pos == square].stack().index.tolist())
                        
                        #go through the square cells except the box/line
                        for ix in inx:
                            if ix[1] != cols:
                            # if ix != (board_pos.index[0],cols) and ix != (board_pos.index[1],cols):
                                try:
                                    temp = cands.iloc[ix].tolist()
                                    temp.remove(val)
                                    cands.iloc[ix] = np.array(temp)
                                    ischanged = 1
                                    print(f"R{ix[0]}C{ix[1]}     Box/Line (col) reduction value {val} removed")
                                except:
                                    pass
        
        
        if ischanged:
            board,cands = solver(board,cands)  

#%% SOLVER FUNCTION
def solver(board,cands):
    board,cands = single_cand(board,cands)
    board,cands = hidden_singles(board,cands)
    board,cands = naked_pairs(board,cands)
    board,cands = hidden_pairs(board,cands)
    board,cands = naked_triples(board,cands)
    board,cands = hidden_triples(board,cands)
    board,cands = pointing_pairs(board,cands)
    box_line(board,cands)
    board,cands = x_wing(board,cands)
    
    return board,cands

#%% RUN THE SOLVER
    
#construct the board

#empty boards
# board = np.zeros((9,9))
# board = pd.DataFrame(
#       [['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
#        ['.', '.', '.', '.', '.', '.', '.', '.', '.']])

#use following to convert board tables to single line string:
# grid = np.array2string(board.replace(".",0).values.flatten()).translate({ord(i): None for i in "[]\n "})

# grids from Andrew Stuart's website
#####SOLVED
# grid = "000004028406000005100030600000301000087000140000709000002010003900000507670400000"
####SOLVED #(moderate in Andrew Stuart website) needs naked triple
# grid = "720096003000205000080004020000000060106503807040000000030800090000702000200430018"
# # board for naked pairs (tough in Andrew Stuart website) needs Y-wing
# grid = "309000400200709000087000000750060230600904008028050041000000590000106007006000104"
# #board for POINTING PAIRS (diabolical in Andrew Stuart website), needs simple colouring
# grid = "000704005020010070000080002090006250600070008053200010400090000030060090200407000"
# # board for xwing example, needs y-wing
# grid = "093004560060003140004608309981345000347286951652070483406002890000400010029800034"
#board for hidden triple (SOLVED)
# grid="300000000970010000600583000200000900500621003008000005000435002000090056000000001"
#board for box/line reduction (simple coloring needed)
# grid="000921003009000060000000500080403006007000800500700040003000000020000700800195000"


# # grids from github
# # https://github.com/sok63/sudoku-1/blob/master/sample/p096_sudoku.txt
# Grid 01 (Simple colouring needed)
# grid = "200000006000602000010090004300009600040000090009500001500010370000408000600000002"
# Grid 02 (3D medusa needed)
# grid = "000050000300284000010000408086003200400000009005700140507000030000637001000020000"
# Grid 03 (SOLVED)
# grid = "000000907000420180000705026100904000050000040000507009920108000034059000507000000"
# # Grid 05 (SOLVED)
# grid = "020810740700003100090002805009040087400208003160030200302700060005600008076051090"
# # Grid 06 (SOLVED)
# grid = "840000000000000000000905001200380040000000005000000000300000820009501000000700000"
# Grid 07 # (Y Wing needed)
# grid = "007000400060070030090203000005047609000000000908130200000705080070020090001000500"
# Grid 26 (SOLVED)
# grid = "500400060009000800640020000000001008208000501700500000000090084003000600060003002"
# Grid 48 (SOLVED)
# grid = "001007090590080001030000080000005800050060020004100000080000030100020079020700400"

#cracking the cryptic LGFL83r67M (hidden quads needed)
# grid = "000000010210003480039800200060304900000000000001607040008002170026700098090000000"
#cracking the cryptic mgp6LprDM8 (simple colouring needed)
# grid = "800000100010790560007108040570020400008010795103050080701003006000000010002001900"
#cracking the cryptic 3gLbRPQ42d (SOLVED)
# grid = "000000700000001080300020004090002060005000800080700050200070003060500000003000000"
#cracking the cryptic JDFGD8p2m3 (diabolic strategies needed)
# grid = "800000300040001000200470000400000000010002070003090005000685000008000120000009003"   
#cracking the cryptic RRf6bgb9GG (SOLVED)
# grid = "609102080000000400502000000000020304100005000020000506000801000000000009805907040"   
#cracking the cryptic BHBjPFJJP4 (Need swordfish)
# grid = "040300600001002090000000000000000000030600900007001020060400300700000008002007010"   
           
board = []

for i in range(81):
    board.append(int(grid[i]))

board = pd.Series(board).replace(0,".")
board = pd.DataFrame(board.values.reshape((9,9)))

board.index = ["A","A","A","B","B","B","C","C","C"]
board.columns = ["A","A","A","B","B","B","C","C","C"]


square_pos = pd.DataFrame([ [1,1,1,2,2,2,3,3,3],
                            [1,1,1,2,2,2,3,3,3],
                            [1,1,1,2,2,2,3,3,3],
                            [4,4,4,5,5,5,6,6,6],
                            [4,4,4,5,5,5,6,6,6],
                            [4,4,4,5,5,5,6,6,6],
                            [7,7,7,8,8,8,9,9,9],
                            [7,7,7,8,8,8,9,9,9],
                            [7,7,7,8,8,8,9,9,9]])

# square_pos = pd.DataFrame(np.full((9,9),np.nan))

# for i in [[0,1,2],[3,4,5],[6,7,8]]:
#     for j in [[0,1,2],[3,4,5],[6,7,8]]:
#         for k in i:
#             for l in j:
#                 square_pos.iloc[k,l] = i,j
            
t1 = time.time()
print_board(board)
cands = candidates(board)
board,cands = solver(board,cands)
print(f"Solving took {time.time()-t1} seconds")
board.index = np.arange(1,10)
board.columns = np.arange(1,10)
print_board(board)
print(f"{(board == '.').sum().sum()} Missing Elements Left in The Board!")

            
   