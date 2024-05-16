import pronouncing
import re
from collections import Counter

def get_phonemes(word):
    phonemes = pronouncing.phones_for_word(word)
    if phonemes:
        return phonemes[0]
    return None

def process_phonetic_patterns(phonetic_patterns):
    # Split each phonetic pattern into its component sounds
    return [pattern.split() for pattern in phonetic_patterns]

def detect_common_phoneme(sentence):
    words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
    phonetic_patterns = [get_phonemes(word) for word in words if get_phonemes(word)]

    # Process phonetic patterns into a list of lists
    phonetic_lists = process_phonetic_patterns(phonetic_patterns)
    unique_phonemes_per_list = [set(sublist) for sublist in phonetic_lists]
    
    # Flatten the list of sets into a single list of phonemes
    all_phonemes = [phoneme for sublist in unique_phonemes_per_list for phoneme in sublist]

    phoneme_counter = Counter(all_phonemes)
    
    # Find the maximum count of any phoneme
    if phoneme_counter:
        max_count = max(phoneme_counter.values())
        most_common_phonemes = [(phoneme, count) for phoneme, count in phoneme_counter.items() if count == max_count]
        return most_common_phonemes
    else:
        return []

def detect_assonance(sentence):
    words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
    if len(words) < 5:
        return 0 
    vowels = "AEIOU"
    count = 0
    mcp = detect_common_phoneme(sentence)
    for p,c in mcp:
        if c/len(words) >= 0.45 and p[0] in vowels:
            print(sentence)
            print(mcp)
            print(" ")
            return 1
    return 0

def detect_consonance(sentence):
    words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
    if len(words) < 5:
        return 0 
    vowels = "AEIOU"
    count = 0
    mcp = detect_common_phoneme(sentence)
    for p,c in mcp:
        if c/len(words) > 0.44 and p[0] not in vowels:
            print(sentence)
            print(mcp)
            print(" ")
            return 1
    return 0

def detect_alliteration(sentence):
    words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
    if len(words) < 5:
        return 0
    phonetic_patterns = [get_phonemes(word) for word in words if get_phonemes(word)]
    alliteration_score = 0 
    phoneme = ""
    for i in range(len(phonetic_patterns) - 1):
        for j in range(3):
            if i + j + 1 <= len(phonetic_patterns) - 1:
                if phonetic_patterns[i][0] == phonetic_patterns[i + j + 1][0]:
                    phoneme = phonetic_patterns[i][0]
                    alliteration_score += 1
                    break

    if alliteration_score / len(words) > 0.4:
        print(sentence)
        print(f"common sound: {phoneme}")
        return 3
    return 0

def detect_diacopes(sentence, excluded_words):
    # Initialize the list of diacopes
    D = []

    # Unique words in the sentence, excluding the excluded words
    S_u = list(set(sentence) - set(excluded_words))

    for word in S_u:
        word_positions = []
        for i in range(len(sentence)):
            if sentence[i] == word and i - 1 not in word_positions:
                word_positions.append(i)

        if len(word_positions) >= 2:
            D.append({'word': word, 'positions': word_positions})

    # Merge diacopes in nearby words
    i = 0
    while i < len(D) - 1:
        power = 0
        for position_a in D[i]['positions']:
            for position_b in D[i + 1]['positions']:
                if abs(position_a - position_b) <= 1:  # Nearby positions
                    power += 1

        if power >= 2 and power == len(D[i + 1]['positions']):
            D[i]['positions'].extend(D[i + 1]['positions'])
            D[i]['positions'] = sorted(list(set(D[i]['positions'])))  # Remove duplicates and sort
            del D[i + 1]
        else:
            i += 1

    return D

def epanalepsis(wordsO, stop_words):
    words = wordsO
    repeat_length = 0
    orig = words
    n = len(words)
    for length in range(1, (n // 2) ):
        if words[:length] == words[-length:] and not set(words[:length]).intersection(stop_words):
            repeat_length = length
    if repeat_length > 0:
        #print("h1")
        return words[:repeat_length] + epanalepsis(words[repeat_length:-repeat_length], stop_words)

    words = words[1:]

    n = len(words)
    for length in range(1, (n // 2) + 1):
        if words[:length] == words[-length:] and not set(words[:length]).intersection(stop_words):
            repeat_length = length
    if repeat_length > 0:
        #print("h2")
        return words[:repeat_length] + epanalepsis(words[repeat_length:-repeat_length], stop_words)
    
    words = words[:len(words) - 1]
    if len(words) > 1:
        n = len(words)
        for length in range(1, (n // 2 + 1)):
            if words[:length] == words[-length:] and not set(words[:length]).intersection(stop_words):
                repeat_length = length
        if repeat_length > 0:
            #print("h3")
            return words[:repeat_length] + epanalepsis(words[repeat_length:-repeat_length], stop_words)

    words = orig[:len(orig) - 1]
    if len(words) > 2:
        n = len(words)
        for length in range(1, (n // 2) + 1):
            if words[:length] == words[-length:] and not set(words[:length]).intersection(stop_words):
                repeat_length = length
        if repeat_length > 0:
            #print("h4")
            return words[:repeat_length] + epanalepsis(words[repeat_length:-repeat_length], stop_words)

    return []

def find_epizeuxis(chapter, stop_words):
    E = []
    current_epizeuxis = None

    def is_stop_word(word):
        return word in stop_words

    def epizeuxis(context):
        return context

    for i in range(len(chapter) - 1):
        sentence1 = chapter[i]
        sentence2 = chapter[i + 1]
        if sentence1 == sentence2 and not is_stop_word(sentence1):
            if current_epizeuxis:
                current_epizeuxis = epizeuxis(context=current_epizeuxis + [sentence2])
            else:
                current_epizeuxis = epizeuxis(context=[sentence1, sentence2])
        else:
            if current_epizeuxis:
                E.append(current_epizeuxis)
                current_epizeuxis = None

    if current_epizeuxis:
        E.append(current_epizeuxis)

    return E


def process_sentences(filename, excluded_words, mode, split_mode):
    count = 0
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
        
    sentences = re.split(r'(?<=[.!?])\s+', text)
    paragraphs = text.split('\n\n')
    
    if split_mode == 1:
        sentences = paragraphs

    print("EPIZEUXIS:")
    result = find_epizeuxis(sentences, excluded_words)
    print(f"{result}")
    print()

    print("DIACOPES:    #")
    for sentence in sentences:
        words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
        
        result = detect_diacopes(words, excluded_words)
        
        if result != []:
            count = count + 1
            print(f"Sentence: {sentence.strip()}")
            print(f"Result: {result}")
            print()
    print("Found " + str(count))
    count = 0
    print("EPANALEPSIS:    #")
    for sentence in sentences:
        words = re.findall(r"\b\w+(?:['.,?!’]*)\b", sentence.lower())
        
        result = epanalepsis(words, excluded_words)
        
        if result != []:
            count = count + 1
            print(f"Sentence: {sentence.strip()}")
            print(f"Result: {result}")
            print()
    print("Found " + str(count))
    count = 0

    print("ALLITERATION: #")
    print()
    for sentence in sentences:
        if detect_alliteration(sentence) > 2:
            print(" ")
            count += 1
    print("Found " + str(count))
    count = 0

    print("ASSONANCE: #")
    print()
    for sentence in sentences:
        count += detect_assonance(sentence)
    
    print("Found " + str(count))
    count = 0

    print("CONSONANCE: #")
    print()
    for sentence in sentences:
        count += detect_consonance(sentence)
    print("Found " + str(count))
        
# Example usage
filename = 'second.txt'
#excluded_words = ["is", "the", "that"]
excluded_words=[]
mode = 1  # Set this to 1 for detect_diacopes, or any other value for epanalepsis
split_mode = 2

process_sentences(filename, excluded_words, mode, split_mode)
