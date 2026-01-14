from django import forms
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
from .models import Listing, Category,UserProfile, ListingReview, ListingComment, Review, SiteReview
from .models import Listing, CONDITION_CHOICES, LISTING_TYPE_CHOICES, LABEL_CHOICES
from django.contrib.auth import get_user_model
User = get_user_model()


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'price',
            'category',

            # location block
            'province',
            'city',
            'location',
            'postal_code',

            # details
            'condition',
            'listing_type',
            'contact_phone',
            'label',

            # main image
            'image',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'A catchy title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your item in detail...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),

            'category': forms.Select(attrs={'class': 'form-select'}),

            'province': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Neighborhood, area, etc.'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),

            'condition': forms.Select(attrs={'class': 'form-select'}),
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 555 123 4567'
            }),
            'label': forms.Select(attrs={'class': 'form-select'}),

            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # показываем только подкатегории
        self.fields['category'].queryset = Category.objects.filter(
            parent__isnull=False,
            is_visible=True
        )


# Форма для загрузки дополнительных изображений
class ListingImageForm(forms.Form):
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Image file"
    )

# Отзыв об объявлении (покупателя)
class ListingReviewForm(forms.ModelForm):
    """Отзыв об объявлении (только для авторизованных)."""
    class Meta:
        model = ListingReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience...'}),
        }

class ReviewForm(forms.ModelForm):
    """Отзыв о продавце (в профиле пользователя)."""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Leave a review...'}
            ),
        }


class ListingCommentForm(forms.ModelForm):
    """Комментарий под объявлением."""
    class Meta:
        model = ListingComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a comment...'}
            ),
        }

class SiteReviewForm(forms.ModelForm):
    class Meta:
        model = SiteReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Leave a review...'}
            ),
        }


class AllAuthSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label="First name",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        label="Last name",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    phone = forms.CharField(
        max_length=20,
        label="Phone (optional)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional phone number'
        })
    )

    agree = forms.BooleanField(
        required=True,
        label="I agree to the Terms & Privacy Policy"
    )

    def clean_agree(self):
        if not self.cleaned_data.get("agree"):
            raise ValidationError("You must agree to the Terms & Privacy Policy.")
        return True

    def save(self, request):
        user = super().save(request)

        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()

        # attach phone to profile if exists
        try:
            profile = user.profile
        except Exception:
            profile = None

        if profile:
            phone = self.cleaned_data.get('phone', '')
            if phone:
                profile.phone = phone
                profile.save()

        return user
