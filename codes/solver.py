# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:40:39 2020

@author: omer.eker
"""

from single_candidate import single_cand
from hidden_singles import hidden_singles
from hidden_pairs_triples_quads import hidden_pairs_triples, hidden_quads
from naked_pairs_triples_quads import naked_pairs_triples, naked_quads
from pointing_pairs import pointing_pairs
from box_line import box_line
from x_wing import x_wing
from y_wing import y_wing
from singles_chains import singles_chains
from xyz_wing import xyz_wing
from swordfish import swordfish


import sys

#%% SOLVER FUNCTION
def new_solver(board,cands,square_pos):
    #run strategies in listed order as long as the board has empty cells (".")
    while True:
        changed = False
        board, cands, square_pos, changed = single_cand(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = hidden_singles(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        # Early dropout
        if not (board == ".").any().any():
            print("COMPLETE!!!!!")
            break

        board, cands, square_pos, changed = naked_pairs_triples(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = hidden_pairs_triples(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = pointing_pairs(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = box_line(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = naked_quads(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = hidden_quads(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = x_wing(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        board, cands, square_pos, changed = y_wing(board,cands,square_pos)   # Refactored2
        if changed:
            continue

        # FW: Quick and dirty optimisation dropout point
        # If we get here it's much much quicker to check whether the puzzle is solved than to go on to singles chains
        if not (board == ".").any().any():
            print("COMPLETE!!!!!")
            break

        board, cands, square_pos, changed = singles_chains(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        # xyz_wing(board,cands,square_pos)  # FW: Broken at present
        # if changed:
        #     continue

        board, cands, square_pos, changed = swordfish(board,cands,square_pos)  # Refactored2
        if changed:
            continue

        if not (board == ".").any().any():
            print("COMPLETE!!!!!")
            break
        else:
            print("Failed!")
            break


def solver(board,cands,square_pos):
    raise RecursionError("Tried to run OG solver, but this is now deprecated")
    #run strategies in listed order as long as the board has empty cells (".")
    if (board==".").any().any():
        single_cand(board,cands,square_pos)
        hidden_singles(board,cands,square_pos)
        naked_pairs_triples(board,cands,square_pos)
        hidden_pairs_triples(board,cands,square_pos)
        pointing_pairs(board,cands,square_pos)
        box_line(board,cands,square_pos)
        naked_quads(board,cands,square_pos)
        hidden_quads(board,cands,square_pos)
        x_wing(board,cands,square_pos)
        y_wing(board,cands,square_pos)
        singles_chains(board,cands,square_pos)
        xyz_wing(board,cands,square_pos)
        swordfish(board,cands,square_pos)
    else:
        print("COMPLETE!!!!!")
        # break
        # sys.exit(0)   # No longer want to exit whole program after completion