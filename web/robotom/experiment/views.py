# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
import logging
import hashlib
import datetime
import random
import requests
import tempfile
import os
from models import Tomograph
from django.shortcuts import get_object_or_404
from django.core import files
import urllib2
import json
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger('django.request')


def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']


def info_once_only(request, msg):
    storage = get_messages(request)
    if msg not in [m.message for m in storage]:
        messages.info(request, msg)


def migrations():
    if len(Tomograph.objects.all()) == 0:
        Tomo = Tomograph(state='off')
        Tomo.save()


@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if tomo.state == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif tomo.state == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')
    if request.method == 'POST':
        if 'on_exp' in request.POST:  # включить томограф
            try:
                answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=100)
                print answer.content
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index'))
            except Timeout as e:
                messages.warning(request,
                                 'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже.')
                logger.error(e)
                return redirect(reverse('experiment:index'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index'))
            if answer_check['success'] == True:
                messages.success(request, u'Томограф включен')
                info_once_only(request, u'Текущее состояние томографа: ожидание')
                tomo.state = 'waiting'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'of_exp' in request.POST:  # выключение томографа
            try:
                answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            except Timeout as e:
                messages.warning(request,
                                 'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже.')
                logger.error(e)
                return redirect(reverse('experiment:index'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index'))
            if answer_check['success'] == True:
                messages.success(request, u'Томограф выключен')
                info_once_only(request, u'Текущее состояние томографа: выключен')
                print tomo.state
                tomo.state = 'off'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
    return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment')
    })


@login_required
@user_passes_test(has_experiment_access)
def experiment_adjustment(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    print tomo.state
    if tomo.state == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif tomo.state == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')
    if request.method == 'POST':
        # if tomo.state == 'waiting' or tomo.state == 'adjustment' :
        if 'move_hor_submit' in request.POST:  # подвинуть по горизонтали
            try:
                info = json.dumps(float(request.POST['move_hor']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-horizontal-position', info,
                                       timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Горизонтальное положение образца изменено.')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
                print tomo.state
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'move_ver_submit' in request.POST:  # подвинуть по вертикали
            try:
                info = json.dumps(float(request.POST['move_ver']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-vertical-position', info,
                                       timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Вертикальное положение образца изменено.')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'rotate_submit' in request.POST:  # повернуть
            try:
                info = json.dumps(float(request.POST['rotate']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-angle-position', info,
                                       timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Образец повернут.')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'reset_submit' in request.POST:  # установить текущее положение за 0
            try:
                answer = requests.get('http://109.234.34.140:5001/tomograph/1/motor/reset-angle-position', timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Текущее положение установлено за 0.')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'text_gate' in request.POST:
            if request.POST['gate_state'] == 'open':  # открыть заслонку
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/open/0', timeout=100)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_adjustment'))
                if answer_check['success'] == True:
                    messages.success(request, u'Заслонка открыта')
                    info_once_only(request, u'Текущее состояние томографа: юстировка')
                    tomo.state = 'adjustment'
                    tomo.save()
                else:
                    logger.error(
                        u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                            answer_check['error']))
                    messages.warning(request,
                                     u'Модуль "Эксперимент" неработает корректно в данный момент. Попробуйте позже {}'.format(
                                         answer_check['error']))
            if request.POST['gate_state'] == 'close':  # закрыть заслонку
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/close/0', timeout=100)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Заслонка закрыта')
                        info_once_only(request, u'Текущее состояние томографа: юстировка')
                        tomo.state = 'adjustment'
                        tomo.save()
                    else:
                        logger.error(
                            u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                answer_check['error']))
                        messages.warning(request,
                                         u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                             answer_check['error']))
        if 'experiment_on_voltage' in request.POST:  # задать напряжение
            info = json.dumps(float(request.POST['voltage']))
            try:
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-voltage', info, timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(
                        u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Напряжение установлено')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'experiment_on_current' in request.POST:  # задать силу тока
            info = json.dumps(float(request.POST['current']))
            try:
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-current', info, timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(
                        u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            print(answer_check)
            if answer_check['success'] == True:
                messages.success(request, u'Сила тока установлена')
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                tomo.state = 'adjustment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))

        if 'picture_exposure_submit' in request.POST:  # preview a picture

            try:
                exposure = request.POST['picture_exposure']
                print(exposure)
                image_url = 'http://109.234.34.140:5001/tomograph/1/detector/get-frame'
                data = json.dumps(float(exposure))
                response = requests.post(image_url, data, stream=True)
                if response.status_code != 200:
                    messages.warning(request, u'Не удалось получить картинку')
                    logger.error(u'Не удалось получить картинку, код ошибки: {}'.format(response.status_code))
                else:
                    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                    file_name = hashlib.sha1(salt + str(request.user.id)).hexdigest() + '.png'
                    temp_file = tempfile.TemporaryFile()
                    for block in response.iter_content(1024 * 8):
                        if not block:
                            break
                        temp_file.write(block)

                    path = default_storage.save(os.path.join(settings.MEDIA_ROOT, file_name), temp_file)
                    return render(request, 'experiment/adjustment.html', {
                        'full_access': (request.user.userprofile.role == 'EXP'),
                        'caption': 'Эксперимент',
                        'preview_path': os.path.join(settings.MEDIA_URL, file_name),
                        'preview': True,
                        'exposure': exposure,
                    })
            except BaseException as e:
                messages.warning(request, u'Не удалось выполнить предпросмотр. Попробуйте повторно')
                logger.error(e)
    return render(request, 'experiment/adjustment.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment')
    })


@login_required
@user_passes_test(has_experiment_access)
def experiment_interface(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if tomo.state == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif tomo.state == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')
    if request.method == 'POST':
        if 'parameters' in request.POST:
            exp_id = uuid.uuid4()
            simple_experiment = json.dumps({
                'experiment id': str(exp_id),
                'specimen': request.POST['name'],
                'tags': request.POST['tags'],
                'experiment parameters':
                    {
                        'advanced': False,
                        'DARK':
                            {
                                'count': int(float(request.POST['dark_quantity'])),
                                'exposure': float(request.POST['dark_exposure'])
                            },
                        'EMPTY':
                            {
                                'count': int(float(request.POST['empty_quantity'])),
                                'exposure': float(request.POST['dark_exposure'])
                            },
                        'DATA':
                            {
                                'step count': int(float(request.POST['data_shots_quantity'])),
                                'exposure': float(request.POST['data_shots_exposure']),
                                'angle step': float(request.POST['data_angle']),
                                'count per step': int(float(request.POST['data_same']))
                            }
                    }
            })
            try:
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/experiment/start', simple_experiment,
                                       timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_interface'))
            except Timeout as e:
                messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
                logger.error(e)
                return redirect(reverse('experiment:index_interface'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_interface'))
            if answer_check['success'] == True:
                messages.success(request, u'Эксперимент успешно начался')
                info_once_only(request, u'Текущее состояние томографа: эксперимент')
                tomo.state = 'experiment'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
        if 'turn_down' in request.POST:
            try:
                answer = requests.get('http://109.234.34.140:5001/tomograph/1/experiment/stop', timeout=100)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_interface'))
            except Timeout as e:
                messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
                logger.error(e)
                return redirect(reverse('experiment:index_interface'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_interface'))
            if answer_check['success'] == True:
                messages.success(request, u'Эксперимент окончен')
                info_once_only(request, u'Текущее состояние томографа: ожидание')
                tomo.state = 'waiting'
                tomo.save()
            else:
                logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
                messages.warning(request,
                                 u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                                     answer_check['error']))
    return render(request, 'experiment/interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment')
    })