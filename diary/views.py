from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from datetime import date, timedelta
from datetime import date as dt_date
import calendar
from .forms import RecordForm
from .models import Record, Mood
import re


def change_username(request):
    if request.method == "POST":
        new_username = (request.POST.get("new_username") or "").strip()
        if not new_username:
            messages.error(request, "新しいユーザー名を入力してください")
        # 変更がない場合
        elif new_username == request.user.username:
            messages.error(request, "現在のユーザー名と同じです")
        # 重複チェック（自分以外）
        elif User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
            messages.error(request, "このユーザー名は既に使用されています")
        else:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "ユーザー名を変更しました")
            return redirect("settings")
    return render(request, "diary/change_username.html")


def change_email(request):
    if request.method == "POST":
        new_email     = (request.POST.get("new_email") or "").strip()
        confirm_email = (request.POST.get("confirm_email") or "").strip()

        # 0文字エラー
        if not new_email:
            messages.error(request, "新しいメールアドレスを入力してください")
        # 現在と同じ（大文字小文字を無視）
        elif (request.user.email or "").lower() == new_email.lower():
            messages.error(request, "現在のメールアドレスと同じです")
        # 形式チェック（簡易）
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", new_email):
            messages.error(request, "正しいメールアドレスの形式で入力してください")
        # 確認用と一致（大文字小文字を無視）
        elif new_email.lower() != confirm_email.lower():
            messages.error(request, "新しいメールアドレスが一致しません")
        # 他ユーザーと重複（大文字小文字を無視）
        elif User.objects.filter(email__iexact=new_email).exclude(pk=request.user.pk).exists():
            messages.error(request, "このメールアドレスは既に使用されています")
        else:
            request.user.email = (new_email or "").strip().lower()
            request.user.save()
            messages.success(request, "メールアドレスを変更しました")
            return redirect("settings")
    return render(request, "diary/change_email.html")


def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "すべての項目を入力してください")
            return redirect("change_password")
        if not request.user.check_password(current_password):
            messages.error(request, "現在のパスワードが正しくありません")
            return redirect("change_password")
        if new_password == current_password:
            messages.error(request, "現在のパスワードと同じです")
            return redirect("change_password")
        if new_password != confirm_password:
            messages.error(request, "新しいパスワードが一致しません")
            return redirect("change_password")
        if not new_password:
            messages.error(request, "新しいパスワードを入力してください")
            return redirect("change_password")
        if len(new_password) < 6:
            messages.error(request, "パスワードは6文字以上にしてください")
            return redirect("change_password")

        request.user.set_password(new_password)
        request.user.save()
        
        update_session_auth_hash(request, request.user)

        messages.success(request, "パスワードを変更しました")
        return redirect("settings")
    return render(request, 'diary/change_password.html')


#ログイン
def login_view(request):
    # すでにログイン中なら、ログイン画面を表示せずホームへ
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "ログインしました")
            return redirect("home")  # ログイン後にカレンダー画面へ
        else:
            messages.error(request, "ユーザー名またはパスワードが間違っています")
    return render(request, "diary/login.html")


#ログイン後操作可
@login_required
def calendar_view(request):
    year = request.GET.get('year')
    month = request.GET.get('month')

    today = date.today()
    if year and month:
        year = int(year)
        month = int(month)
    else:
        year = today.year
        month = today.month

    # 月曜始まり
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    # 表示範囲（前後月を含む最初〜最後）
    first_display = month_days[0][0]
    last_display  = month_days[-1][-1]

    # このユーザーの「記録がある日」を一括取得
    recorded_qs = (
        Record.objects
        .filter(user=request.user, date__gte=first_display, date__lte=last_display)
        .values_list("date", flat=True)
    )
    recorded_dates = list(set(recorded_qs))
    
    records = (
        Record.objects
        .filter(user=request.user, date__gte=first_display, date__lte=last_display)
        .select_related("mood")
        .values("date", "mood__color", "photo")
    )

    records_by_date = {
        r["date"].isoformat(): {
            "color": r["mood__color"],   
            "photo": r["photo"], 
        }
        for r in records
    }

    # 前月・次月
    first_day  = date(year, month, 1)
    prev_month = first_day - timedelta(days=1)
    next_month = date(year + (month // 12), (month % 12) + 1, 1)

    context = {
        "year": year,
        "month": month,
        "month_days": month_days,
        "today": today,
        "prev_month": prev_month,
        "next_month": next_month,
        "recorded_dates": recorded_dates,  
        "records_by_date": records_by_date, 
    }
    return render(request, "diary/calendar.html", context)


@login_required
def record_view(request, selected_date=None):
    # --- 日付の取得（?date=YYYY-MM-DD） ---
    date_str = request.GET.get("date", "") or selected_date or ""
    initial_date = None
    try:
        if date_str:
            initial_date = dt_date.fromisoformat(date_str)
    except ValueError:
        pass

    # --- 既存レコード（編集判定） ---
    existing = None
    if initial_date:
        existing = Record.objects.filter(user=request.user, date=initial_date).first()

    # --- Mood マスター（5色） ---
    DEFAULT_COLORS = ["red", "orange", "yellow", "green", "blue"]
    if not Mood.objects.exists():
        Mood.objects.bulk_create([Mood(color=c) for c in DEFAULT_COLORS])

    order = Case(
        *[When(color=c, then=idx) for idx, c in enumerate(DEFAULT_COLORS)],
        default=len(DEFAULT_COLORS),
        output_field=IntegerField(),
    )
    moods = Mood.objects.order_by(order, "id")

    if request.method == "POST":
        # ★ 記録削除処理
        if "delete_record" in request.POST:
            if existing:
                if existing.photo:
                    existing.photo.delete(save=False)
                existing.delete()
                messages.success(request, "記録を削除しました")
            else:
                messages.info(request, "削除する記録はありません")
            return redirect("calendar")

        # ★ 写真削除処理（モーダルからのPOST）
        if "remove_photo" in request.POST:
            if existing and existing.photo:
                existing.photo.delete(save=False)
                existing.photo = None
                existing.save(update_fields=["photo"])
                messages.success(request, "写真を削除しました")
            # initial_date が None の場合に isoformat() で落ちないように分岐
            if initial_date:
                return redirect("record_with_date", selected_date=initial_date.isoformat())
            else:
                return redirect("record")

        # 通常の保存処理
        form = RecordForm(request.POST, request.FILES, instance=existing)

        # “日付未入力”を検出
        post_date_str = (request.POST.get("date") or "").strip()
        if not post_date_str:
            messages.error(request, "日付を入力してください")
            
            form = RecordForm(request.POST, instance=existing)
            
            # 入力保持
            selected_mood_id = request.POST.get("mood") or None
            return render(request, "diary/record.html", {
                "form": form,  
                "moods": moods,
                "selected_mood_id": selected_mood_id,
                "has_record": bool(existing),
                "display_date": initial_date,
                "reset_photo": True, 
            })

        if form.is_valid():
            data = form.cleaned_data
            save_date = data.get("date")
            if not save_date:
                messages.error(request, "日付を入力してください")
                selected_mood_id = request.POST.get("mood") or None
                return render(request, "diary/record.html", {
                    "form": form,
                    "moods": moods,
                    "selected_mood_id": selected_mood_id,
                    "has_record": bool(existing),
                    "display_date": initial_date,
                    "reset_photo": False,
                })

            mood_value = data.get("mood")
            note_value = (data.get("note") or "").strip()
            uploaded   = data.get("photo")
            removing   = bool(request.POST.get("remove_photo"))

            # ③ 既存バリデーション：気分/メモ/写真のいずれか必須
            if not mood_value and not note_value and not (uploaded or (existing and existing.photo and not removing)):
                messages.error(request, "気分・メモ・写真のいずれか1つは入力してください")
                return redirect("record_with_date", selected_date=save_date.isoformat())

            # 写真の決定ロジック
            if removing and existing and existing.photo:
                existing.photo.delete(save=False)

            if removing:
                photo_value = None
            else:
                if uploaded:
                    photo_value = uploaded
                else:
                    photo_value = existing.photo if existing and existing.photo else None

            Record.objects.update_or_create(
                user=request.user, date=save_date,
                defaults={
                    "mood":  data.get("mood") or None,
                    "note":  data.get("note", ""),
                    "photo": photo_value,
                }
            )
            messages.success(request, "記録を保存しました")
            return redirect("calendar")

    else:
        form = RecordForm(instance=existing) if existing else RecordForm(initial={"date": initial_date})

    # 選択中 mood
    if request.method == "POST":
        selected_mood_id = request.POST.get("mood") or None
    else:
        selected_mood_id = str(existing.mood_id) if existing and existing.mood_id else None

    return render(request, "diary/record.html", {
        "form": form,
        "moods": moods,
        "selected_mood_id": selected_mood_id,
        "has_record": bool(existing),
        "display_date": initial_date,
    })


@login_required
def record_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if record.photo:
        record.photo.delete(save=False)
    record.delete()
    messages.success(request, "記録を削除しました")
    return redirect("calendar")

@login_required
def photo_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if record.photo:
        record.photo.delete(save=False)
        record.photo = None
        record.save()
        messages.success(request, "写真を削除しました")
    else:
        messages.info(request, "削除できる写真がありません")
    return redirect("calendar")  # ★ カレンダーに戻す


@login_required
def settings_view(request):
    return render(request, "diary/settings.html")


def logout_view(request):
    logout(request)
    messages.success(request, "ログアウトしました")
    return redirect("login")  # ログアウト後はログイン画面へ


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        # 入力チェック
        if not username or not email or not password or not confirm_password:
            messages.error(request, "すべての項目を入力してください")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "パスワードが一致しません")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "このユーザー名は既に使用されています")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "このメールアドレスは既に使用されています")
            return redirect("signup")

        # ユーザー作成
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        messages.success(request, "アカウントを作成しました")
        return redirect("home")

    return render(request, "diary/signup.html")


