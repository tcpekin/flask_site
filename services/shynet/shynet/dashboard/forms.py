from allauth.account.admin import EmailAddress
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import Service, User


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "link",
            "respect_dnt",
            "collect_ips",
            "ignored_ips",
            "ignore_robots",
            "hide_referrer_regex",
            "origins",
            "collaborators",
            "script_inject",
        ]
        widgets = {
            "name": forms.TextInput(),
            "origins": forms.TextInput(),
            "ignored_ips": forms.TextInput(),
            "respect_dnt": forms.RadioSelect(
                choices=[(True, _("Yes")), (False, _("No"))]
            ),
            "collect_ips": forms.RadioSelect(
                choices=[(True, _("Yes")), (False, _("No"))]
            ),
            "ignore_robots": forms.RadioSelect(
                choices=[(True, _("Yes")), (False, _("No"))]
            ),
            "hide_referrer_regex": forms.TextInput(),
            "script_inject": forms.Textarea(attrs={"class": "font-mono", "rows": 5}),
        }
        labels = {
            "origins": _("Allowed origins"),
            "respect_dnt": _("Respect DNT"),
            "ignored_ips": _("Ignored IP addresses"),
            "ignore_robots": _("Ignore robots"),
            "hide_referrer_regex": _("Hide specific referrers"),
            "script_inject": _("Additional injected JS"),
        }
        help_texts = {
            "name": _("What should the service be called?"),
            "link": _("What's the service's primary URL?"),
            "origins": _(
                "At what origins does the service operate? Use commas to separate multiple values. This sets CORS headers, so use '*' if you're not sure (or don't care)."
            ),
            "respect_dnt": _(
                "Should visitors who have enabled <a href='https://en.wikipedia.org/wiki/Do_Not_Track'>Do Not Track</a> be excluded from all data?"
            ),
            "ignored_ips": _(
                "A comma-separated list of IP addresses or IP ranges (IPv4 and IPv6) to exclude from tracking (e.g., '192.168.0.2, 127.0.0.1/32')."
            ),
            "ignore_robots": _(
                "Should sessions generated by bots be excluded from tracking?"
            ),
            "hide_referrer_regex": _(
                "Any referrers that match this <a href='https://regexr.com/'>RegEx</a> will not be listed in the referrer summary. Sessions will still be tracked normally. No effect if left blank."
            ),
            "script_inject": _(
                "Optional additional JavaScript to inject at the end of the Shynet script. This code will be injected on every page where this service is installed."
            ),
        }

    collect_ips = forms.BooleanField(
        help_text=_("IP address collection is disabled globally by your administrator.")
        if settings.BLOCK_ALL_IPS
        else _(
            "Should individual IP addresses be collected? IP metadata (location, host, etc) will still be collected."
        ),
        widget=forms.RadioSelect(choices=[(True, _("Yes")), (False, _("No"))]),
        initial=False if settings.BLOCK_ALL_IPS else True,
        required=False,
        disabled=settings.BLOCK_ALL_IPS,
    )

    def clean_collect_ips(self):
        collect_ips = self.cleaned_data["collect_ips"]
        # Forces collect IPs to be false if it is disabled globally
        return False if settings.BLOCK_ALL_IPS else collect_ips

    collaborators = forms.CharField(
        help_text=_(
            "Which users on this Shynet instance should have read-only access to this service? (Comma separated list of emails.)"
        ),
        required=False,
    )

    def clean_collaborators(self):
        collaborators = []
        users_to_emails = (
            {}
        )  # maps users to the email they are listed under as a collaborator
        for collaborator_email in self.cleaned_data["collaborators"].split(","):
            email = collaborator_email.strip()
            if email == "":
                continue
            collaborator_email_linked = EmailAddress.objects.filter(
                email__iexact=email
            ).first()
            if collaborator_email_linked is None:
                raise forms.ValidationError(f"Email '{email}' is not registered")
            user = collaborator_email_linked.user
            if user in collaborators:
                raise forms.ValidationError(
                    f"The emails '{email}' and '{users_to_emails[user]}' both correspond to the same user"
                )
            users_to_emails[user] = email
            collaborators.append(collaborator_email_linked.user)
        return collaborators

    def get_initial_for_field(self, field, field_name):
        initial = super(ServiceForm, self).get_initial_for_field(field, field_name)
        if field_name == "collaborators":
            return ", ".join([user.email for user in (initial or [])])
        return initial