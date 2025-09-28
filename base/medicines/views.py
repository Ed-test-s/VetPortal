from django.shortcuts import render, get_object_or_404, redirect
from .models import Medicine

from orders.models import Favorite

from pharmacies.models import PharmacyMedicine

from reviews.models import Review, ReviewImage
from reviews.forms import ReviewForm, ReviewImageForm
from django.db.models import Avg, Count

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse




def home(request):
    latest_medicines = Medicine.objects.order_by('-id')[:9]

    # пометим для каждого лекарства — в избранном ли оно у текущего пользователя
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        favorite_ids = Favorite.objects.filter(user=request.user.profile).values_list("medicine_id", flat=True)
        for med in latest_medicines:
            med.is_favorite = med.id in favorite_ids
    else:
        for med in latest_medicines:
            med.is_favorite = False

    context = {
        "latest_medicines": latest_medicines
    }
    return render(request, "medicines/home.html", context)


def medicine_list(request):
    return render(request, "medicines/list.html")


def medicine_detail(request, slug):
    """
    Страница конкретного лекарства:
      - объект Medicine
      - is_favorite (для текущего пользователя)
      - список PharmacyMedicine (аптеки, цены, наличие)
    """
    medicine = get_object_or_404(Medicine, slug=slug)

    pharmacies = (
        PharmacyMedicine.objects
        .filter(medicine=medicine)
        .select_related("pharmacy")
    )

    # флаг избранного
    is_favorite = False
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        is_favorite = Favorite.objects.filter(
            user=request.user.profile,
            medicine=medicine
        ).exists()

    # средний рейтинг и кол-во отзывов
    stats = Review.objects.filter(medicine=medicine).aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id")
    )
    avg_rating = stats["avg_rating"] or 0
    total_reviews = stats["total_reviews"]

    context = {
        "medicine": medicine,
        "pharmacies": pharmacies,
        "is_favorite": is_favorite,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "stars_range": range(1, 6),
    }
    return render(request, "medicines/detail.html", context)


def medicine_reviews(request, slug):
    medicine = get_object_or_404(Medicine, slug=slug)
    reviews = (
        Review.objects
        .filter(medicine=medicine)
        .select_related("user")
        .order_by("-created_at")
    )
    return render(request, "reviews/reviews.html", {
        "medicine": medicine,
        "reviews": reviews,
        "stars_range": range(1, 6),
    })



@login_required
def add_review(request, slug):
    medicine = get_object_or_404(Medicine, slug=slug)

    # Проверка: уже есть отзыв от этого юзера?
    if Review.objects.filter(user=request.user.profile, medicine=medicine).exists():
        return HttpResponse(
            f"<script>alert('Вы уже оставляли отзыв на этот товар!');"
            f"window.location.href='{redirect('medicine_reviews', slug=medicine.slug).url}';</script>"
        )

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        image_form = ReviewImageForm(request.POST, request.FILES)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user.profile
            review.medicine = medicine
            review.save()

            for file in request.FILES.getlist("image"):
                ReviewImage.objects.create(review=review, image=file)

            return redirect("medicine_reviews", slug=medicine.slug)
    else:
        review_form = ReviewForm()
        image_form = ReviewImageForm()

    return render(
        request,
        "reviews/add_review.html",
        {"review_form": review_form, "image_form": image_form, "medicine": medicine},
    )



def review_detail(request, slug, review_id):
    medicine = get_object_or_404(Medicine, slug=slug)
    review = get_object_or_404(Review, id=review_id, medicine=medicine)
    return render(request, "reviews/review_detail.html", {
        "medicine": medicine,
        "review": review,
    })


