import logging
from datetime import datetime
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import escape

from .models import Booking

logger = logging.getLogger(__name__)

DEFAULT_PRIMARY_COLOR = "#4f46e5"
DEFAULT_ACCENT_COLOR = "#7c3aed"


def _get_recipient_email(booking: Booking) -> Optional[str]:
    if booking.attendee_email:
        return booking.attendee_email
    user_input = booking.user_input or {}
    return user_input.get('email')


def _resolve_display_timezone(booking: Booking):
    user_input = booking.user_input or {}
    tz_key = (
        user_input.get("timezone")
        or user_input.get("time_zone")
        or user_input.get("timeZone")
    )
    if tz_key:
        try:
            return ZoneInfo(tz_key)
        except ZoneInfoNotFoundError:
            logger.warning(
                "Unknown timezone '%s' provided for booking %s",
                tz_key,
                booking.id,
            )
    return timezone.get_default_timezone()


def _normalize_hex(color: Optional[str], fallback: str) -> str:
    if not color:
        return fallback
    hex_color = color.strip()
    if not hex_color.startswith("#"):
        hex_color = f"#{hex_color}"
    hex_color = hex_color.lower()
    if len(hex_color) == 4:
        hex_color = "#" + "".join(ch * 2 for ch in hex_color[1:])
    if len(hex_color) != 7:
        return fallback
    allowed = "0123456789abcdef"
    if not all(ch in allowed for ch in hex_color[1:]):
        return fallback
    return hex_color


def _hex_to_rgba(color: str, alpha: float, fallback: str) -> str:
    hex_color = color.lstrip("#")
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except (ValueError, IndexError):
        return fallback
    return f"rgba({r}, {g}, {b}, {alpha})"


def _format_schedule(booking: Booking):
    user_input = booking.user_input or {}
    selected_date = user_input.get("selected_date")
    selected_time = user_input.get("selected_time")
    display_tz = _resolve_display_timezone(booking)

    if selected_date and selected_time:
        time_str = selected_time
        if len(time_str) == 5:
            time_str = f"{time_str}:00"
        dt_str = f"{selected_date}T{time_str}"
        try:
            local_dt = datetime.fromisoformat(dt_str)
            if local_dt.tzinfo is None:
                local_dt = local_dt.replace(tzinfo=display_tz)
            schedule_line = local_dt.strftime("%A, %B %d, %Y at %I:%M %p")
            tz_label = local_dt.tzname() or getattr(display_tz, "key", str(display_tz))
            return schedule_line, tz_label
        except ValueError:
            schedule_line = f"{selected_date} at {selected_time}"
            tz_label = getattr(display_tz, "key", str(display_tz))
            return schedule_line, tz_label

    appointment_dt = booking.date
    if timezone.is_naive(appointment_dt):
        appointment_dt = timezone.make_aware(appointment_dt, timezone=timezone.utc)
    local_dt = appointment_dt.astimezone(display_tz)

    schedule_line = local_dt.strftime("%A, %B %d, %Y at %I:%M %p")
    tz_label = local_dt.tzname() or getattr(display_tz, "key", str(display_tz))
    return schedule_line, tz_label


def _build_text_body(
    attendee_name: str,
    meeting_owner: str,
    meeting_title: str,
    status_line: str,
    schedule_line: str,
    timezone_label: str,
    booking_status: str,
    notes: Optional[str],
    meeting_link: Optional[str],
) -> str:
    lines = [
        f"Hi {attendee_name or 'there'},",
        "",
        f"Your booking for {meeting_title} with {meeting_owner} has been {status_line}.",
        f"Scheduled for: {schedule_line} ({timezone_label})",
        f"Current status: {booking_status}",
    ]

    if meeting_link:
        lines.extend(["", f"Join Google Meet: {meeting_link}"])

    if notes:
        lines.extend(["", "Notes:", notes])

    lines.extend(
        [
            "",
            "If you have any questions, just reply to this email.",
            "",
            "Best regards,",
            meeting_owner,
        ]
    )

    return "\n".join(lines)


def _build_html_body(
    attendee_name: str,
    meeting_owner: str,
    meeting_title: str,
    status_line: str,
    schedule_line: str,
    timezone_label: str,
    booking_status: str,
    notes: Optional[str],
    meeting_link: Optional[str],
    *,
    primary_color: str,
    accent_color: str,
    primary_light: str,
    accent_light: str,
) -> str:
    notes_block = ""
    if notes:
        formatted_notes = escape(notes).replace("\n", "<br>")
        notes_block = f"""
            <tr>
              <td style="padding: 20px 32px; background-color: {escape(accent_light)};">
                <h3 style="margin: 0 0 8px; font-size: 15px; color: {escape(accent_color)}; font-weight: 600;">Notes</h3>
                <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #334155;">{formatted_notes}</p>
              </td>
            </tr>
        """

    meeting_link_block = ""
    if meeting_link:
        meeting_link_block = f"""
            <tr>
              <td style="padding:12px 36px;">
                <a href="{escape(meeting_link)}" style="display:inline-block; padding:14px 24px; border-radius:999px; background:linear-gradient(135deg,{escape(primary_color)},{escape(accent_color)}); color:#ffffff; text-decoration:none; font-weight:600; font-size:15px;">
                  Join Google Meet
                </a>
                <p style="margin:12px 0 0; font-size:14px; color:#64748b;">
                  Or copy this link into your browser:<br>
                  <a href="{escape(meeting_link)}" style="color:{escape(primary_color)}; text-decoration:none;">{escape(meeting_link)}</a>
                </p>
              </td>
            </tr>
        """

    html = f"""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{escape(meeting_title)} booking {escape(status_line)}</title>
  </head>
  <body style="margin:0; padding:0; background-color:{escape(primary_light)}; font-family:'Helvetica Neue', Arial, sans-serif; color:#0f172a;">
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;">
      <tr>
        <td align="center" style="padding:36px 16px;">
          <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:640px; background-color:#ffffff; border-radius:24px; overflow:hidden; box-shadow:0 18px 45px {escape(primary_light)}; border:1px solid {escape(accent_light)};">
            <tr>
              <td style="padding:40px; background:linear-gradient(135deg,{escape(primary_color)},{escape(accent_color)});">
                <p style="margin:0 0 6px; font-size:13px; letter-spacing:1.4px; text-transform:uppercase; color:rgba(255,255,255,0.72); font-weight:600;">Booking {escape(status_line)}</p>
                <h1 style="margin:0; font-size:28px; line-height:1.3; color:#ffffff;">{escape(meeting_title)}</h1>
                <p style="margin:16px 0 0; font-size:15px; color:rgba(255,255,255,0.88); line-height:1.6;">
                  Your booking with {escape(meeting_owner)} has been {escape(status_line)}.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 36px 12px;">
                <p style="margin:0; font-size:16px; color:#334155; line-height:1.6;">Hi <strong>{escape(attendee_name or 'there')}</strong>,</p>
                <p style="margin:16px 0 0; font-size:15px; color:#475569; line-height:1.7;">
                  Here are your meeting details:
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:12px 36px 28px;">
                <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:separate; border-spacing:0 12px;">
                  <tr>
                    <td style="padding:18px 24px; background-color:{escape(primary_light)}; border-radius:16px;">
                      <p style="margin:0; font-size:12px; text-transform:uppercase; letter-spacing:1px; color:{escape(primary_color)}; font-weight:600;">Scheduled for</p>
                      <p style="margin:6px 0 0; font-size:18px; font-weight:600; color:#0f172a;">{escape(schedule_line)}</p>
                      <p style="margin:4px 0 0; font-size:14px; color:#64748b;">Timezone: {escape(timezone_label)}</p>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:18px 24px; background-color:{escape(accent_light)}; border-radius:16px;">
                      <p style="margin:0; font-size:12px; text-transform:uppercase; letter-spacing:1px; color:{escape(accent_color)}; font-weight:600;">Status</p>
                      <p style="margin:6px 0 0; font-size:18px; font-weight:600; color:#0f172a;">{escape(booking_status)}</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            {notes_block}
            {meeting_link_block}
            <tr>
              <td style="padding:24px 32px 40px;">
                <p style="margin:0; font-size:14px; color:#64748b; line-height:1.7;">
                  Need to make changes or have questions? Just reply to this email.
                </p>
                <p style="margin:18px 0 0; font-size:15px; color:#334155; line-height:1.7;">
                  Warm regards,<br>
                  <strong>{escape(meeting_owner)}</strong>
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    return html


def send_booking_email(booking: Booking, *, action: Literal["created", "updated"] = "created") -> None:
    """
    Send a confirmation email to the attendee.
    """
    recipient = _get_recipient_email(booking)
    if not recipient:
        logger.info("Skipping email for booking %s: no recipient found", booking.id)
        return

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or getattr(settings, "EMAIL_HOST_USER", "")
    if not from_email:
        logger.warning("Cannot send email for booking %s: DEFAULT_FROM_EMAIL not configured", booking.id)
        return

    meeting_title = booking.meeting_page.title if booking.meeting_page else "Meeting"
    meeting_owner = (
        booking.meeting_page.user.get_full_name()
        if booking.meeting_page and callable(getattr(booking.meeting_page.user, "get_full_name", None))
        else booking.meeting_page.user.email if booking.meeting_page else "Host"
    )

    schedule_line, timezone_label = _format_schedule(booking)
    status_line = "confirmed" if action == "created" else "updated"
    subject = f"Your booking is {status_line} - {meeting_title}"
    meeting_link = getattr(settings, "GOOGLE_MEET_LINK", None)

    theme = getattr(booking.meeting_page, "theme", {}) or {}
    primary_color = _normalize_hex(theme.get("primaryColor"), DEFAULT_PRIMARY_COLOR)
    accent_color = _normalize_hex(theme.get("accentColor"), DEFAULT_ACCENT_COLOR)
    primary_light = _hex_to_rgba(primary_color, 0.12, "rgba(79, 70, 229, 0.12)")
    accent_light = _hex_to_rgba(accent_color, 0.18, "rgba(124, 58, 237, 0.18)")

    text_body = _build_text_body(
        booking.attendee_name or "there",
        meeting_owner,
        meeting_title,
        status_line,
        schedule_line,
        timezone_label,
        booking.status.title(),
        booking.notes,
        meeting_link,
    )

    html_body = _build_html_body(
        booking.attendee_name or "there",
        meeting_owner,
        meeting_title,
        status_line,
        schedule_line,
        timezone_label,
        booking.status.title(),
        booking.notes,
        meeting_link,
        primary_color=primary_color,
        accent_color=accent_color,
        primary_light=primary_light,
        accent_light=accent_light,
    )

    try:
        send_mail(
            subject,
            text_body,
            from_email,
            [recipient],
            fail_silently=False,
            html_message=html_body,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send booking %s email to %s", booking.id, recipient)

