from django.shortcuts import render
from service import run_query


def search(request): 
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip() 
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'main/search.html', {'result_list': result_list})

