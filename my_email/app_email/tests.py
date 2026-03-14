from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Email


class EmailModelTest(TestCase):
    """Тесты для модели Email."""
    
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='password123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='password123'
        )
    
    def test_send_email(self):
        """Тест отправки письма."""
        email = Email.send_email(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тестовое письмо',
            body='Текст тестового письма'
        )
        
        # Проверяем, что письмо создано для получателя
        self.assertEqual(email.subject, 'Тестовое письмо')
        self.assertEqual(email.recipient, self.recipient)
        self.assertEqual(email.sender, self.sender)
        self.assertEqual(email.folder, 'inbox')
        self.assertFalse(email.read)
        
        # Проверяем, что создана копия для отправителя
        sent_copy = Email.objects.filter(
            sender=self.sender,
            folder='sent',
            subject='Тестовое письмо'
        ).first()
        self.assertIsNotNone(sent_copy)
        self.assertTrue(sent_copy.read)
        
        # Проверяем, что slug уникальны для каждой записи
        self.assertNotEqual(email.slug, sent_copy.slug)
    
    def test_move_to_folder(self):
        """Тест перемещения письма в другую папку."""
        email = Email.send_email(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тест',
            body='Текст'
        )
        
        result = email.move_to_folder('trash')
        self.assertTrue(result)
        email.refresh_from_db()
        self.assertEqual(email.folder, 'trash')
    
    def test_move_to_invalid_folder(self):
        """Тест перемещения в несуществующую папку."""
        email = Email.send_email(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тест',
            body='Текст'
        )
        
        result = email.move_to_folder('invalid_folder')
        self.assertFalse(result)
    
    def test_mark_as_read(self):
        """Тест отметки письма как прочитанного."""
        email = Email.send_email(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тест',
            body='Текст'
        )
        
        self.assertFalse(email.read)
        email.mark_as_read()
        email.refresh_from_db()
        self.assertTrue(email.read)
    
    def test_email_str(self):
        """Тест строкового представления."""
        email = Email.send_email(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тема',
            body='Текст'
        )
        self.assertEqual(str(email), f"Тема → {self.recipient}")


class EmailViewTest(TestCase):
    """Тесты для представлений."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='password123'
        )
    
    def test_root_redirect_authenticated(self):
        """Тест перенаправления авторизованного пользователя."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
    
    def test_root_redirect_anonymous(self):
        """Тест перенаправления неавторизованного пользователя."""
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('login'))
    
    def test_inbox_access_denied(self):
        """Тест доступа к чужим письмам."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('inbox', kwargs={'username': 'otheruser'}))
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
    
    def test_inbox_authenticated(self):
        """Тест доступа к своим письмам."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('inbox', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email/inbox.html')
    
    def test_email_list_drafts(self):
        """Тест просмотра черновиков."""
        self.client.login(username='testuser', password='password123')
        
        # Создаём черновик
        Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Черновик',
            body='Текст',
            folder='drafts'
        )
        
        response = self.client.get(reverse('email_list', kwargs={
            'username': 'testuser',
            'folder': 'drafts'
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Черновик')
    
    def test_email_list_trash(self):
        """Тест просмотра корзины (письма отправителя и получателя)."""
        self.client.login(username='testuser', password='password123')
        
        # Письмо, где testuser - получатель
        Email.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Входящее в корзине',
            body='Текст',
            folder='trash'
        )
        
        # Письмо, где testuser - отправитель
        Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Исходящее в корзине',
            body='Текст',
            folder='trash'
        )
        
        response = self.client.get(reverse('email_list', kwargs={
            'username': 'testuser',
            'folder': 'trash'
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Входящее в корзине')
        self.assertContains(response, 'Исходящее в корзине')
    
    def test_compose_email_get(self):
        """Тест страницы написания письма."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('compose', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email/compose.html')
    
    def test_compose_email_post_success(self):
        """Тест успешной отправки письма."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('compose', kwargs={'username': 'testuser'}), {
            'recipient': 'otheruser',
            'subject': 'Тестовое письмо',
            'body': 'Привет! Это тестовое письмо.'
        })
        self.assertRedirects(response, reverse('email_list', kwargs={'username': 'testuser', 'folder': 'sent'}))
        
        # Проверяем, что письмо создано
        email = Email.objects.filter(subject='Тестовое письмо').first()
        self.assertIsNotNone(email)
        self.assertEqual(email.sender, self.user)
        self.assertEqual(email.recipient, self.other_user)
    
    def test_compose_email_to_self(self):
        """Тест отправки письма самому себе."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('compose', kwargs={'username': 'testuser'}), {
            'recipient': 'testuser',
            'subject': 'Тест',
            'body': 'Текст'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Нельзя отправить письмо самому себе')
    
    def test_compose_email_invalid_recipient(self):
        """Тест отправки письма несуществующему пользователю."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('compose', kwargs={'username': 'testuser'}), {
            'recipient': 'nonexistent',
            'subject': 'Тест',
            'body': 'Текст'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь с таким username не найден')
    
    def test_email_detail(self):
        """Тест просмотра письма."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        # Письмо должно быть непрочитанным
        self.assertFalse(email.read)
        
        response = self.client.get(reverse('email_detail', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email/detail.html')
        
        # Проверяем, что письмо отмечено как прочитанное (получатель открыл)
        email.refresh_from_db()
        self.assertTrue(email.read)
    
    def test_email_detail_sender_view(self):
        """Тест: отправитель открывает письмо — оно НЕ должно отмечаться как прочитанное."""
        self.client.login(username='otheruser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        # Письмо должно быть непрочитанным
        self.assertFalse(email.read)
        
        # Отправитель открывает письмо
        response = self.client.get(reverse('email_detail', kwargs={
            'username': 'otheruser',
            'email_slug': email.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        
        # Письмо НЕ должно быть отмечено как прочитанное
        email.refresh_from_db()
        self.assertFalse(email.read)
    
    def test_email_detail_draft_view(self):
        """Тест: просмотр черновика НЕ должен отмечать его как прочитанное."""
        self.client.login(username='testuser', password='password123')
        
        draft = Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Черновик',
            body='Текст',
            folder='drafts',
            read=False
        )
        
        response = self.client.get(reverse('email_detail', kwargs={
            'username': 'testuser',
            'email_slug': draft.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        
        # Черновик НЕ должен измениться
        draft.refresh_from_db()
        self.assertFalse(draft.read)
    
    def test_move_email_to_trash(self):
        """Тест перемещения письма в корзину."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        response = self.client.post(reverse('move_email', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }), {'folder': 'trash'})
        
        self.assertRedirects(response, reverse('email_detail', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        email.refresh_from_db()
        self.assertEqual(email.folder, 'trash')
    
    def test_delete_email_from_inbox(self):
        """Тест: удаление из входящих перемещает в корзину."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        response = self.client.post(reverse('delete_email', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
        
        # Письмо должно быть в корзине, а не удалено
        email_exists = Email.objects.filter(slug=email.slug).exists()
        self.assertTrue(email_exists)
        
        email.refresh_from_db()
        self.assertEqual(email.folder, 'trash')
    
    def test_delete_email_from_trash(self):
        """Тест: удаление из корзины удаляет навсегда."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст',
            folder='trash'
        )
        
        response = self.client.post(reverse('delete_email', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
        
        # Письмо должно быть удалено
        email_exists = Email.objects.filter(slug=email.slug).exists()
        self.assertFalse(email_exists)
    
    def test_delete_email_independent_copies(self):
        """Тест: удаление письма у получателя не влияет на копию отправителя."""
        self.client.login(username='testuser', password='password123')
        
        # Отправляем письмо
        Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        # Находим копию отправителя
        sender_copy = Email.objects.filter(
            sender=self.other_user,
            folder='sent',
            subject='Тест'
        ).first()
        
        self.assertIsNotNone(sender_copy)
        sender_slug = sender_copy.slug
        
        # Получатель (testuser) удаляет письмо у себя
        recipient_email = Email.objects.get(
            recipient=self.user,
            folder='inbox',
            subject='Тест'
        )
        
        self.client.post(reverse('delete_email', kwargs={
            'username': 'testuser',
            'email_slug': recipient_email.slug
        }))
        
        # Копия отправителя должна остаться в sent
        sender_copy.refresh_from_db()
        self.assertEqual(sender_copy.folder, 'sent')
        self.assertTrue(Email.objects.filter(slug=sender_slug).exists())
    
    def test_recipient_cannot_move_to_drafts(self):
        """Тест: получатель не может переместить письмо в черновики."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        response = self.client.post(reverse('move_email', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }), {'folder': 'drafts'})
        
        # Должна быть ошибка, письмо не должно переместиться
        self.assertRedirects(response, reverse('email_detail', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        email.refresh_from_db()
        self.assertNotEqual(email.folder, 'drafts')
        self.assertEqual(email.folder, 'inbox')
    
    def test_move_email(self):
        """Тест перемещения письма."""
        self.client.login(username='testuser', password='password123')
        
        email = Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Тест',
            body='Текст'
        )
        
        response = self.client.post(reverse('move_email', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }), {'folder': 'trash'})
        
        self.assertRedirects(response, reverse('email_detail', kwargs={
            'username': 'testuser',
            'email_slug': email.slug
        }))
        
        email.refresh_from_db()
        self.assertEqual(email.folder, 'trash')
    
    def test_register_view_get(self):
        """Тест страницы регистрации."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_register_view_post_success(self):
        """Тест успешной регистрации."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Testpassword123!',
            'password2': 'Testpassword123!'
        })
        
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'newuser'}))
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_view_authenticated(self):
        """Тест регистрации авторизованного пользователя."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
    
    def test_search_emails(self):
        """Тест поиска писем."""
        self.client.login(username='testuser', password='password123')
        
        Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Важное письмо',
            body='Содержит важный текст'
        )
        
        Email.send_email(
            sender=self.other_user,
            recipient=self.user,
            subject='Обычное письмо',
            body='Обычный текст'
        )
        
        response = self.client.get(reverse('inbox', kwargs={'username': 'testuser'}), {'q': 'Важное'})
        emails_list = list(response.context['emails'])
        self.assertEqual(len(emails_list), 1)
        self.assertEqual(emails_list[0].subject, 'Важное письмо')


class RegistrationFormTest(TestCase):
    """Тесты для формы регистрации."""
    
    def test_registration_form_valid(self):
        """Тест валидной формы регистрации."""
        from .forms import RegistrationForm
        
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'Testpassword123!',
            'password2': 'Testpassword123!'
        })
        
        self.assertTrue(form.is_valid())
    
    def test_registration_form_password_mismatch(self):
        """Тест несовпадения паролей."""
        from .forms import RegistrationForm

        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'password123',
            'password2': 'password456'
        })

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class DraftEmailTest(TestCase):
    """Тесты для функционала черновиков."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Testpassword123!'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='Testpassword123!'
        )
    
    def test_save_as_draft(self):
        """Тест сохранения письма в черновики."""
        self.client.login(username='testuser', password='Testpassword123!')
        
        response = self.client.post(reverse('compose', kwargs={'username': 'testuser'}), {
            'recipient': 'otheruser',
            'subject': 'Черновик письма',
            'body': 'Это черновик, который нужно сохранить.',
            'save_draft': '1'
        })
        
        self.assertRedirects(response, reverse('email_list', kwargs={'username': 'testuser', 'folder': 'drafts'}))
        
        draft = Email.objects.filter(subject='Черновик письма', folder='drafts').first()
        self.assertIsNotNone(draft)
        self.assertEqual(draft.sender, self.user)
        self.assertEqual(draft.recipient, self.other_user)
    
    def test_edit_draft_get(self):
        """Тест страницы редактирования черновика."""
        self.client.login(username='testuser', password='Testpassword123!')
        
        draft = Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Старый черновик',
            body='Старый текст',
            folder='drafts'
        )
        
        response = self.client.get(reverse('edit_draft', kwargs={
            'username': 'testuser',
            'email_slug': draft.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email/edit_draft.html')
        self.assertContains(response, 'Старый черновик')
    
    def test_edit_draft_save(self):
        """Тест сохранения отредактированного черновика."""
        self.client.login(username='testuser', password='Testpassword123!')
        
        draft = Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Старый черновик',
            body='Старый текст',
            folder='drafts'
        )
        
        response = self.client.post(reverse('edit_draft', kwargs={
            'username': 'testuser',
            'email_slug': draft.slug
        }), {
            'recipient': 'otheruser',
            'subject': 'Обновлённый черновик',
            'body': 'Обновлённый текст',
            'save_draft': '1'
        })
        
        self.assertRedirects(response, reverse('email_list', kwargs={'username': 'testuser', 'folder': 'drafts'}))
        
        draft.refresh_from_db()
        self.assertEqual(draft.subject, 'Обновлённый черновик')
        self.assertEqual(draft.body, 'Обновлённый текст')
        self.assertEqual(draft.folder, 'drafts')
    
    def test_edit_draft_send(self):
        """Тест отправки отредактированного черновика."""
        self.client.login(username='testuser', password='Testpassword123!')
        
        draft = Email.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Черновик',
            body='Текст черновика',
            folder='drafts'
        )
        
        response = self.client.post(reverse('edit_draft', kwargs={
            'username': 'testuser',
            'email_slug': draft.slug
        }), {
            'recipient': 'otheruser',
            'subject': 'Отправленное письмо',
            'body': 'Отправленный текст'
        })
        
        self.assertRedirects(response, reverse('email_list', kwargs={'username': 'testuser', 'folder': 'sent'}))
        
        # Проверяем, что черновик стал отправленным
        draft.refresh_from_db()
        self.assertEqual(draft.folder, 'sent')
        
        # Проверяем, что письмо создано для получателя
        received = Email.objects.filter(
            recipient=self.other_user,
            folder='inbox',
            subject='Отправленное письмо'
        ).first()
        self.assertIsNotNone(received)
    
    def test_edit_draft_not_owner(self):
        """Тест редактирования чужого черновика."""
        self.client.login(username='testuser', password='Testpassword123!')
        
        draft = Email.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Чужой черновик',
            body='Чужой текст',
            folder='drafts'
        )
        
        response = self.client.get(reverse('edit_draft', kwargs={
            'username': 'testuser',
            'email_slug': draft.slug
        }))
        
        self.assertRedirects(response, reverse('inbox', kwargs={'username': 'testuser'}))
