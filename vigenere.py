import numpy as np
import sys

if (len(sys.argv) < 2):
    print("""usage:
    python vigenere [ciphertext file]""")
    sys.exit(0)

# List corisponding to the occurence frequencies within the english alphabet
alpha_freqs = np.array([ .08167, .01492, .02782, .04253, .12702, .02228, 
                         .02015, .06094, .06966, .00153, .00772, .04025, 
                         .02406, .06749, .07507, .01929, .00095, .05987, 
                         .06327, .09056, .02758, .00978, .02360, .00150, 
                         .01974, .00074 ])

# The 26x26 matrix of freqency shifts
freq_shifts = np.hstack([np.roll(alpha_freqs,i).reshape(26,1) for i in range(0,26)])

def get_cipher_text(file):
    """Does preprocessing on ciphertext. Note: Assumes all capitals.

    Args:
        file (file): File containing the ciphertext to be read.

    Returns:
        Array of ints 0-25 representing A-Z respectivly.
    """
    ciphertext=file.read().replace('\n', '')
    ciphertext = np.array([ord(c) for c in ciphertext]) - 65
    return ciphertext

def get_shifts(ciphertext, shift_max=16):
    """Finds number of coincidences for each shift amount.

    Args:
        ciphertext (int array): Array representing the ciphertext.
        shift_max (int, optional): Max shift that will be checked for coincidences.

    Returns:
        Array of ints corrisponding to the coincidence counts for each `i+1` shift.
    """
    return np.array([np.sum(ciphertext == np.roll(ciphertext, i)) for i in range(1,shift_max+1)])   

def get_buckets(ciphertext, key_length):
    """Breaks ciphertext into buckets for each key character

    Args:
        ciphertext (int array): Array representing the ciphertext.
        key_length (int): The size of the key.

    Returns:
        Array of int arrays. Each int array represents parts of the ciphertext 
        corresponding to each key character.
    """
    return [ciphertext[i::key_length] for i in range(0, key_length)]

def ints_to_string(ch):
    """Converts int arrays to strings of lowercase letters.

    Args:
        ch (int array): The int array to be converted
    
    Returns:
        A string of lowercase characters.
    """
    return ''.join([chr(c+97) for c in ch])

def get_key(buckets):
    """Returns the key based off the character frequencies inside
    each bucket.

    Discussion:
        Per Trappe & Washington, W * A_i yeilds some P, where W and A_i 
        are vectors of length 26, and P is a single value representing the likelihood of the shift being i.

        This may be extended to matrix mulitplication, where W is a Lx26 matrix and A a 26x26 matrix.
        Each of the L rows in W represents one frequency bucket for part of the L length key.
        Each i'th column (or row if you want to think of it like that, it's transform is equal) of A represents
        the frequesncies shifted by i (AKA A_i).
        Their product, WxA yeilds an Lx26 vector, representing the probabilities for each 26 shifts across 
        each L key shifts.


    Args:
        buckets (int array array): The buckets of characters for each key shift.

    Returns:
        An int array of the key shifts.
    
    """
    cipher_freqs = np.array([[np.sum(ct[ct == c])/len(ct) for c in range(0,26)] for ct in buckets])
    R = cipher_freqs.dot(freq_shifts)
    return [np.argmax(r) for r in R]

def decode(ciphertext, key):
    """Decodes the chiphertext given a key.

    Args:
        ciphertext (int array): Array representing the ciphertext.
        key (int array): Array of shifts.

    Returns:
        An int array representing the decoded plaintext.
    """
    return [(26+ciphertext[i] - key[i%len(key)]) % 26 for i in range(0, len(ciphertext))]

def get_top_shifts(shifts, N=3):
    """Gets the top shift amounts based on coincidence counts.
       Deprecated: Not used after the list was printed in order of coincidence.

    Args:
        shifts (int array): Coincidence counts for shifts.
        N (int, optional): Number of top shifts to return.
    
    Returns:
        An int array of the top slections for key lengths
    """
    top = np.array([])
    a = np.arange(0,len(shifts))
    for i in range(0,N):
        n = np.argmax(shifts[a])
        top = np.append(top,a[n]+1)
        a = a[a != a[n]]
    return top

with open(sys.argv[1], 'r') as file:
    key_max = 16
    ciphertext = get_cipher_text(file)

    shifts = get_shifts(ciphertext, shift_max=16)
    for i in np.argsort(shifts)[::-1]:
        print(f"Shift {i+1}: {shifts[i]} coincidences.")

    #print(f"Suggested lengths:")
    #print(get_top_shifts(shifts, 5))
    key_length = int(input("\nEnter a key length to try: "))


    buckets = get_buckets(ciphertext, key_length)

    key = get_key(buckets)
    print(f"\nKey: {ints_to_string(key)}")
    print(ints_to_string(decode(ciphertext, key)))
