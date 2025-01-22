import json
import post


def open_db():
    result = []
    f = open('static/posts/db.json', 'r', encoding='utf-8')
    db = json.load(f)
    f.close()
    for i in db:
        attachments = []
        for j in i.get('attachments'):
            attachments.append(j.get('url'))
        result.append(post.Post(i.get('id'), i.get('name'), i.get('price'), i.get('area'), i.get('description'),
                                attachments))
    return result
