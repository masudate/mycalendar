from django import forms
from .models import Record, Mood


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["date", "mood", "note", "photo"]
        labels = {
            "date": "Date",
            "mood": "気分",
            "note": "メモ",
            "photo": "写真",
        }
        widgets = {
            "date":  forms.DateInput(attrs={"type": "date"}),
            "mood":  forms.Select(attrs={"id": "mood"}),
            "note":  forms.Textarea(attrs={"rows": 4, "placeholder": "メモ"}),
            "photo": forms.ClearableFileInput(attrs={
                "id": "photo-input",
                "accept": "image/*",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 気分は任意（未選択OK）
        self.fields["mood"].required = False
        # 並びやすく取得（赤→橙→黄→緑→青の順整列は views でやっていれば不要）
        self.fields["mood"].queryset = Mood.objects.all().order_by("id")
        self.fields["mood"].empty_label = "（未選択）"
        # 念のため（モデルが blank=True でもフォーム側でも任意に）
        if "photo" in self.fields:
            self.fields["photo"].required = False

    # 空文字が来たら None にして保存する（ForeignKey で安全）
    def clean_mood(self):
        m = self.cleaned_data.get("mood")
        return m or None
