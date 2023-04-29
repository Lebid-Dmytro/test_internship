import itertools

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from nltk import Tree

# функція генерує фрази зі структурного дерева
def generate_phrases(tree):
    phrases = []
    for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
        if len(subtree.leaves()) > 1:
            phrases.append(subtree.leaves())
    return phrases

# функція генерує всі можливі перестановки фраз
def permute_phrases(phrases):
    permutations = []
    for combo in itertools.permutations(phrases):
        permutations.append(list(combo))
    return permutations

# генерації перефразувань
@csrf_exempt
def paraphrase(request):
    try:
        tree_str = request.GET.get('tree', '')
        if not tree_str:
            return HttpResponseBadRequest('Tree parameter is missing')
        tree = Tree.fromstring(tree_str)
        phrases = generate_phrases(tree)
        permutations = permute_phrases(phrases)
        limit = int(request.GET.get('limit', 20))
        paraphrases = []
        for i, p in enumerate(permutations):
            if i == limit:
                break
            new_tree = tree.copy(deep=True)
            phrase_index = 0
            for subtree in new_tree.subtrees(filter=lambda t: t.label() == 'NP'):
                if len(subtree.leaves()) > 1:
                    new_leaves = p[phrase_index]
                    subtree.set_label(' '.join(new_leaves))
                    phrase_index += 1
            paraphrases.append({'tree': str(new_tree)})
        return JsonResponse({'paraphrases': [str(tree).replace('\\n', '') for tree in paraphrases]})
    except Exception as e:
        return HttpResponseBadRequest(str(e))
