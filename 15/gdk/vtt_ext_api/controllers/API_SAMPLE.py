
ADD_DOC_API_SAMPLE = {
    'type': 'url',
    'data': [
        {
            'name': 'This is title of web page 01',
            'url': 'http://www.webpage1.com',
            'description': 'Here is description',
            'note': 'Note input here, longer than description, with multi line',
            'image': '',
            'category_id': 5,
            'category_name': '',
            'category_parent_id': False,
            'tags': ['chrome', 'hit'],
            'ref_id': 100
        },
        {
            'name': 'This is title of web page 02',
            'url': 'http://www.webpage2.com',
            'image': '',
            'description': '',
            'note': '',
            'category_id': False,
            'category_name': 'This new category',
            'category_parent_id': 3,
            'tags': [],
            'ref_id': False
        }
    ]
}

LIST_DOC_API_SAMPLE = {
    'name': '',
    'limit': False
}

DOC_RESULT_SAMPLE = {
    'success': True,
    'message': 'Success',
    'results': [
        {
            'name': 'This is title of web page 01',
            'url': 'http://www.webpage1.com',
            'description': 'Here is description',
            'note': 'Note input here, longer than description, with multi line',
            'tags': ['chrome', 'hit'],
        },
        {
            'name': 'This is title of web page 02',
            'url': 'http://www.webpage2.com',
            'description': 'Here is description 002',
            'note': 'Note input here',
            'tags': [],
        }
    ]
}

ADD_CATEGORY_API_SAMPLE = {
    'name': 'Photoshop',
    'parent_id': 3,
    'ref_id': False
}

LIST_CATEGORY_API_SAMPLE = {
    'name': '',
    'limit': False
}

CATEGORY_RESULT_SAMPLE = {
    'success': True,
    'message': 'Success',
    'results': [
        {
            'id': 5,
            'ref_id': 100,
            'name': 'Category 01',
            'parent_id': 3,
            'refparent_id': 95
        },
        {
            'id': 4,
            'ref_id': 99,
            'name': 'Category -2',
            'parent_id': 3,
            'refparent_id': 95
        }
    ]
}