from django.http import HttpResponseRedirect
# from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic


from .models import Question, Choice

'''
las vistas se definen como funciones dentro del archivo views.py
esto es, cada vista es una una función dentro de views.py
'''

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]

    
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.htm', context)


# def detail(request, question_id):
#     # try:
#     #     '''get the object by question_id'''
#     #     question = Question.objects.get(pk=question_id)
#     # except Question.DoesNotExist:
#     #     raise Http404('Question does not exist')
#     # return render(request, 'polls/detail.htm', {'question': question})

#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.htm', {'question': question})

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.htm', {'question': question})


class IndexView(generic.ListView):
    template_name = 'polls/index.htm'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.htm'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.htm'

def vote(request, question_id):
    '''as a parameters takes a request object and a question_id from the url
    then, save into the question variable an object or 404, for this, search
    with the ORM for a Question object that has a pk as the passed in the url
    if get_object_or_404 return an object then set a choice object as a value for the
    attribute of the question in selected_choice'''
    question = get_object_or_404(Question, pk=question_id)
    try:
        '''choice question.choice_set relate to every single choice that
        has the question as fk, so, if we pass as a parameter the pk=request.POST['choice']
        we get the instance of the choice model class selected
        choice_set was renamed as related_choices
        the get method here act like a where sql clauss'''
        selected_choice = question.related_choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.htm', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
