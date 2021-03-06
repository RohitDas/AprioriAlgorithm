from __future__ import division
import sys
import os
from hash_tree import Node

LEVEL_TO_FREQUENT_ITEMSETS_MAP = None
ITEMS_TO_INDEX_MAP = None

def read_csv(filepath):
	'''Read transactions from csv_file specified by filepath
	Args:
		filepath (str): the path to the file to be read

	Returns:
		list: a list of lists, where each component list is a list of string representing a transaction

	'''

	transactions = []
	with open(filepath, 'r') as f:
		lines = f.readlines()
		for line in lines:
			transactions.append(line.strip().split(',')[:-1])
	return transactions

def get_k1_itemsets(
            items_to_enumerate_map,
            transactions, 
            minsup):
        """
            Function to generate the 1 element itemsets whose support count is >= minusp
        """
        item_to_support_count = {}
        for transaction in transactions:
            #enumerated_transaction = map(lambda x: items_to_enumerate_map[x], transaction)
            for item in transaction:
                if item not in item_to_support_count:
                    item_to_support_count[item] = 1
                else:
                    item_to_support_count[item] += 1

        #Calculate infrequent items
        infrequent_items = filter(lambda x: item_to_support_count[x] < minsup*len(transactions), item_to_support_count.keys())
        for infrequent_item in infrequent_items:
            item_to_support_count.pop(infrequent_item, None)
        return item_to_support_count

def enumerate_items(transactions):
    """
        Enemerate the items of the transaction.
    """
    items = set()
    for transaction in transactions:
        items.update(transaction)
    sorted_items = sorted(items)
    
    items_to_enumerate_map, index_to_items_map = {}, {}
    for index, sorted_item in enumerate(sorted_items):
        items_to_enumerate_map.update({
            sorted_item: index
        })
        index_to_items_map.update({
            index: sorted_item
        })
    return items_to_enumerate_map, index_to_items_map


def apriori_gen(F_1,
                F_k,
                k):
        """
            This function has 2 parts, 
            1. Candidate Generation using the F_k * F_1 method
            2. Candidate pruning
        """
        print("Generating candidates for k = " + str(k))
        #Candidate Generation
        candidate_itemsets = {}
        for itemset in F_k:
            itemset = set([itemset]) if k == 2 else set(itemset)
            for item in F_1:
                if not itemset.intersection(set([item])):
                    candidate_itemsets.update({
                        tuple(sorted(itemset.union({item}))) : 0
                    })
       
        print("Candidates before pruning: ", len(candidate_itemsets))

        #Candidate Pruning
        candidates_to_prune = []
        for candidate_itemset in candidate_itemsets:
            for i in range(k):
                item_to_remove = candidate_itemset[i]
                itemset_to_check = tuple(sorted(set(candidate_itemset).difference(set([item_to_remove]))))
                itemset_to_check = itemset_to_check[0] if k == 2 else itemset_to_check
                if itemset_to_check not in F_k:
                    candidates_to_prune.append(candidate_itemset)

        for candidate_to_prune in candidates_to_prune:
            candidate_itemsets.pop(candidate_to_prune, None)
        
        print("Candidates after pruning: ", len(candidate_itemsets))

        return candidate_itemsets


def return_itemsets_for_transaction(transaction,
                                      k, prior):
    """
        This builds the hash tree of a transaction for the purpose of support
        counting.
    """
    if len(transaction) < k:
        return tuple([])
    if  k == 1:
        return [ tuple(prior + [t]) for t in transaction]
    else:
        itemsets = []
        for i in range(len(transaction)-k+1):
                #get elements starting from that position.
                new_prior = prior + [transaction[i]]
                itemsets += return_itemsets_for_transaction(transaction[i+1:], k-1, new_prior)
        return itemsets

def build_candidate_hash_tree(candidates,k):
    hash_tree = Node(k,5,5,False,False,True,0)
    hash_tree.add_elements(candidates)
    hash_tree.visualize()
    return hash_tree


def update_support_counts(itemsets,
                          support_count_hash_tree,
                          candidates_K):
    for itemset in itemsets:
        if support_count_hash_tree.search(itemset):
            candidates_K[itemset] += 1

def support_counting(transactions,
                     candidates_K, k):

    support_count_hash_tree = build_candidate_hash_tree(candidates_K.keys(), k)
    for transaction in transactions:
        possible_k_itemsets_for_transaction = return_itemsets_for_transaction(transaction, k, [])
        update_support_counts(possible_k_itemsets_for_transaction, 
                support_count_hash_tree, candidates_K)


def candidate_elimination(candidates_K,
                          minsup):
    """
        This function eliminates those candidates whose support is less than minsup
    """
    infrequent_itemsets = []
    for key, value in candidates_K.iteritems():
        if value < minsup:
            infrequent_itemsets.append(key)

    for infrequent_item in infrequent_itemsets:
            candidates_K.pop(infrequent_item, None)

def aggregrated_frequent_items(level_to_frequent_itemsets_map,
                               index_to_items_map):
    frequent_items = []
    for level, level_hash in level_to_frequent_itemsets_map.iteritems():
        if level == 1:
            frequent_items += map(lambda x: [index_to_items_map[x]], level_hash.keys())
        else:
            frequent_items += map(lambda x: map(lambda y: index_to_items_map[y],x), level_hash.keys())
    print len(frequent_items), frequent_items
    return frequent_items

# To be implemented
def generate_frequent_itemset(transactions, minsup):
	'''Generate the frequent itemsets from transactions
	Args:
		transactions (list): a list of lists, where each component list is a list of string representing a transaction
		minsup (float): specifies the minsup for mining

	Returns:
		list: a list of frequent itemsets and each itemset is represented as a list string

	Example:
		Output: [['margarine'], ['ready soups'], ['citrus fruit','semi-finished bread'], ['tropical fruit','yogurt','coffee'], ['whole milk']]
		The meaning of the output is as follows: itemset {margarine}, {ready soups}, {citrus fruit, semi-finished bread}, {tropical fruit, yogurt, coffee}, {whole milk} are all frequent itemset

	'''
        global LEVEL_TO_FREQUENT_ITEMSETS_MAP, ITEMS_TO_INDEX_MAP
        print len(transactions),minsup
        #Enumerate the items from the transaction
        items_to_enumerate_map, index_to_items_map = enumerate_items(transactions)
        enumerated_transactions = map(lambda transaction: sorted(map(lambda x: items_to_enumerate_map[x], transaction)), 
                                            transactions)
        #Generate k = 1 itemsets
        k = 1
        #F_1 = get_k1_itemsets(items_to_enumerate_map, transactions, minsup)
        F_1 = get_k1_itemsets(items_to_enumerate_map, enumerated_transactions, minsup)
        level_to_frequent_itemsets_map = {}
        level_to_frequent_itemsets_map.update({
            1: F_1
        })

        F_k = F_1
        while F_k:
            k += 1
            candidates_K = apriori_gen(F_1, F_k, k)
            support_counting(enumerated_transactions, candidates_K, k)
            candidate_elimination(candidates_K, minsup*len(enumerated_transactions))
            level_to_frequent_itemsets_map.update({
                k: candidates_K
            })
            F_k = candidates_K
        LEVEL_TO_FREQUENT_ITEMSETS_MAP = level_to_frequent_itemsets_map
        ITEMS_TO_INDEX_MAP = items_to_enumerate_map
        return aggregrated_frequent_items(level_to_frequent_itemsets_map,
                                          index_to_items_map)


def get_one_item_consequent(frequent_itemset):
    one_item_consequents = []
    for item in frequent_itemset:
        one_item_consequents.append(set([item]))
    return one_item_consequents

def get_support(frequent_itemset):
    global LEVEL_TO_FREQUENT_ITEMSETS_MAP, ITEMS_TO_INDEX_MAP
    S = len(frequent_itemset)
    print(LEVEL_TO_FREQUENT_ITEMSETS_MAP[S])
    print(frequent_itemset)
    enumerated_frequent_itemset = tuple(sorted([ITEMS_TO_INDEX_MAP[item] for item in frequent_itemset]))
    if S ==  1:
        enumerated_frequent_itemset = enumerated_frequent_itemset[0]
    print("********")
    print(LEVEL_TO_FREQUENT_ITEMSETS_MAP[S][enumerated_frequent_itemset]), enumerated_frequent_itemset
    return LEVEL_TO_FREQUENT_ITEMSETS_MAP[S].get(enumerated_frequent_itemset, 0)

def apriori_gen_rule(frequent_itemset,H_m):
    consequent_length = len(H_m[0])
    print(consequent_length)
    completed_rules = []
    print(frequent_itemset)
    for consequent in H_m:
        completed_rules.append([frequent_itemset.difference(consequent), consequent])
    print completed_rules

    new_rules = {}
    for i in range(H_m):
        for j in range(j, H_m):
            antecedent_a = completed_rules[i]
            antecedent_b = completed_rules[j]
            intersection_a_b = antecedent_a.intersection(antecedent_b)
            if len(intersection_a_b)  == (consequent_length-1):
                new_consequent = frequent_itemset.difference(intersection_a_b)
                new_rules.update({
                    tuple(new_consequent): 1
                })
    return new_rules.keys()

def ap_genrules(frequent_itemset,
                H_1,
                minconf):
    k = len(frequent_itemset)
    m = len(H_1[0])
    H_m  = H_1
    rules = []
    if k > m + 1:
        H_m = apriori_gen_rule(H_m)
        H_m_new = []
        for h_m in H_m:
            confidence = get_support(frequent_itemset)/get_support(frequent_itemset.difference(h_m))
            print("Conf: ", confidence)
            if confidence >= minconf:
                rules.append(h_m)
                H_m_new.append(h_m)
        rules += ap_genrules(frequent_itemset, H_m_new)
    else:
        for h_m in H_m:
            confidence = get_support(frequent_itemset)/get_support(frequent_itemset.difference(h_m))
            print("Conf: ", confidence)
            if confidence >= minconf:
                rules.append(h_m)
    return rules

# To be implemented
def generate_association_rules(transactions, minsup, minconf):
	'''Mine the association rules from transactions
	Args:
		transactions (list): a list of lists, where each component list is a list of string representing a transaction
		minsup (float): specifies the minsup for mining
		minconf (float): specifies the minconf for mining

	Returns:
		list: a list of association rule, each rule is represented as a list of string

	Example:
		Output: [['root vegetables', 'rolls/buns','=>', 'other vegetables'],['root vegetables', 'yogurt','=>','other vegetables']]
		The meaning of the output is as follows: {root vegetables, rolls/buns} => {other vegetables} and {root vegetables, yogurt} => {other vegetables} are the two associated rules found by the algorithm
	

	'''
        frequent_itemsets = generate_frequent_itemset(transactions, minsup)
        association_rules = []
        for frequent_itemset in frequent_itemsets:
            if len(frequent_itemset) >= 2:
                print("Frequent Itemsets")
                print(frequent_itemset)
                H_1 = get_one_item_consequent(set(frequent_itemset))
                rules = ap_genrules(set(frequent_itemset), H_1, minconf)
                print("Rules")
                print(rules)
                for rule in rules:
                    association_rules.append(list(set(frequent_itemset).difference(rule)) + ["=>"] + [list(rule)])
        print(association_rules)            
	return [[]]


def main():

	if len(sys.argv) != 3 and len(sys.argv) != 4:
		print("Wrong command format, please follwoing the command format below:")
		print("python assoc-rule-miner-template.py csv_filepath minsup")
		print("python assoc-rule-miner-template.py csv_filepath minsup minconf")
		exit(0)

	
	if len(sys.argv) == 3:
		transactions = read_csv(sys.argv[1])
		result = generate_frequent_itemset(transactions, float(sys.argv[2]))

		# store frequent itemsets found by your algorithm for automatic marking
		with open('.'+os.sep+'Output'+os.sep+'frequent_itemset_result.txt', 'w') as f:
			for items in result:
				output_str = '{'
				for e in items:
					output_str += e
					output_str += ','

				output_str = output_str[:-1]
				output_str += '}\n'
				f.write(output_str)

	elif len(sys.argv) == 4:
		transactions = read_csv(sys.argv[1])
		minsup = float(sys.argv[2])
		minconf = float(sys.argv[3])
		result = generate_association_rules(transactions, minsup, minconf)

		# store associative rule found by your algorithm for automatic marking
		with open('.'+os.sep+'Output'+os.sep+'assoc-rule-result.txt', 'w') as f:
			for items in result:
				output_str = '{'
				for e in items:
					if e == '=>':
						output_str = output_str[:-1]
						output_str += '} => {'
					else:
						output_str += e
						output_str += ','

				output_str = output_str[:-1]
				output_str += '}\n'
				f.write(output_str)


main()
