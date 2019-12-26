from django.shortcuts import render, reverse
from django.http import HttpResponse
from django.views import View
from .service import run_query


def search(request): 
    result_list = []

    if request.method == 'GET':
        query = request.GET.get('q', '') # request.POST['query'].strip() 
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'main/search.html', {'result_list': result_list, 'query': query})


# class SearchView(View):
#     # template_name = "pages/home.html"
#     success_url = reverse('search:q')

#     def get_success_url(self):
#         success_url = super().get_success_url()
#         return '{0}?search={1}'.format(success_url, self.form.cleaned_data['search'])

# home = SearchView.as_view()

# class ResultView(View):
#     def get(self, request, *args, **kwargs):
#         search_string = request.GET.get('search', '')
#         result_list = run_query(search_string)