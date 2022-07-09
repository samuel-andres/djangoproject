from django.http import HttpResponseRedirect
# from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone


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
    '''por defecto el context_object_name es el nombre del modelo en minúscula underscore
    list'''
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        '''Question.objects.filter(pub_date__lte=timezone.now()) returns a queryset containing Questions whose pub_date is less than or equal to - that is, earlier than or equal to - timezone.now.'''
        questions_with_at_lest_one_choice = Question.objects.filter(pk__in=[choice.question.pk for choice in Choice.objects.all()])
        '''
        for question in Question.objects.all():
            for choice in Choice.objects.all():
                if question.pk in choice.question.pk:
                    return True
        '''

        last_5_questions = questions_with_at_lest_one_choice.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


        return last_5_questions





class DetailView(generic.DetailView):
    ''' por defect el template_name es el nombre del modelo en minúscula underscore
    detail.html'''
    model = Question
    template_name = 'polls/detail.htm'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.htm'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())    

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
