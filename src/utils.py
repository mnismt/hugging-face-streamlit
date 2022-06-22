def flatten(A):
    rt = []
    for i in A:
        if isinstance(i, list):
            rt.extend(flatten(i))
        else:
            rt.append(i)
    return rt


def keep_or_delete_label(review_text, DELETE_WORDS, KEEP_WORDS):
    DELETE_WORDS = flatten(DELETE_WORDS)
    KEEP_WORDS = flatten(KEEP_WORDS)
    is_keep = True

    for delete_word in DELETE_WORDS:
        found = delete_word in review_text
        review_text = review_text.replace(delete_word, '')
        if found:
            is_keep = False

    for keep_word in KEEP_WORDS:
        if keep_word in review_text:
            is_keep = True
            break

    return is_keep
