# Integrate Firebase App Check + the `askGita` chat function into BhagavadGita (V2 KMP app)

Paste this to the app agent.

---

A Gita chat backend is already deployed. Your job is to make the app able to call it: add
Firebase App Check on both platforms, add the Cloud Functions client, and build the call +
response handling. Do not change the backend or Firestore security rules.

## Backend facts (already live — do not change)

- Firebase project: `gitaapp-24519`
- Callable function: **`askGita`**, region **`asia-south1`** (not the default `us-central1` —
  calling without the region gives a not-found error)
- It rejects every call unless **both** are true:
  1. the user is signed in and their Firebase ID token has `email_verified == true`
  2. the request carries a valid **Firebase App Check** token (`enforceAppCheck: true`)
- Current app stack (checked): GitLive Firebase `dev.gitlive:*` **2.6.0** (auth, firestore,
  config, messaging, analytics, crashlytics), Koin, Compose Multiplatform. iOS links Firebase
  through Swift Package Manager (`firebase-ios-sdk`). Auth providers: Google and Apple.

## 1. App Check

GitLive has **no App Check module** (`dev.gitlive:firebase-app-check` does not exist), so
initialise App Check **natively on each platform**. Once it is initialised, the native
Functions SDK that GitLive wraps attaches the App Check token to every callable request
automatically — no token plumbing in shared code.

### Android
- Add `com.google.firebase:firebase-appcheck-playintegrity` for release and
  `com.google.firebase:firebase-appcheck-debug` for debug builds (versions from the Firebase
  BoM already on the classpath).
- In the `Application` class (`BhagavadGitaApplication`), after Firebase is initialised and
  **before** any other Firebase call, install the provider factory:
  - debug build → `DebugAppCheckProviderFactory.getInstance()`
  - release build → `PlayIntegrityAppCheckProviderFactory.getInstance()`
- Never ship the debug provider in a release build.

### iOS
- Add the **FirebaseAppCheck** product from the existing `firebase-ios-sdk` SPM package.
- In `iOSApp.swift`, set the provider factory **before** `FirebaseApp.configure()`:
  - `#if DEBUG` → `AppCheckDebugProviderFactory()`
  - release → a factory returning `AppAttestProvider(app:)` (iOS 14+).
- Add the **App Attest** capability to the iosApp target (entitlement
  `com.apple.developer.devicecheck.appattest-environment` = `production`).

### Console steps — list these for the user, you can't do them
- Firebase console → App Check → register the **Android** app with **Play Integrity** (the
  app's SHA-256 signing fingerprints — upload key and Play App Signing key — must be in
  Project settings).
- Register the **iOS** app with **App Attest** (needs the Apple Team ID).
- Debug builds print a **debug token** to the log on first launch; it must be added under App
  Check → Manage debug tokens, or every debug call is rejected.

## 2. Cloud Functions client

- Add `dev.gitlive:firebase-functions:2.6.0` to `commonMain`.
- iOS: link the **FirebaseFunctions** product the same way the other Firebase iOS products are
  linked. Note: the iosApp SPM products currently list only Analytics, Auth, Core, Crashlytics
  and RemoteConfig — if Firestore/Messaging reach iOS some other way, follow that; if they
  don't, report it to the user as a pre-existing gap rather than silently changing it.
- Call it with the region:
  ```kotlin
  Firebase.functions(region = "asia-south1").httpsCallable("askGita").invoke(request)
  ```
  and decode `result.data<AskGitaResponse>()`.

## 3. Request / response contract

```kotlin
@Serializable data class AskGitaRequest(
    val query: String,                         // 1..1000 chars
    val character: String = "krishna",         // "krishna" | "arjun"
    val language: String = "en",               // "en" | "hi" | "be" | "ka"  — the app language
    val history: List<ChatTurn> = emptyList(), // server keeps only the last 6
)
@Serializable data class ChatTurn(val role: String, val content: String) // role: "user" | "model"

@Serializable data class AskGitaResponse(
    val onTopic: Boolean,      // false = off-topic; answer is a gentle redirect, sources = []
    val selfHarm: Boolean,     // true = user may be in crisis; answer ends with helplines
    val answer: String,        // already in the requested language and character
    val language: String,
    val character: String,
    val sources: List<Source>, // verses the answer used (empty when off-topic / selfHarm)
    val helplines: List<Helpline>, // non-empty only when selfHarm
)
@Serializable data class Source(val slokId: String, val chapter: Int, val verse: Int, val score: Double)
@Serializable data class Helpline(val name: String, val number: String, val note: String)
```

The server does all the work (retrieval, off-topic detection, self-harm detection, language,
persona). Do not re-implement or second-guess any of it in the app.

## 4. UI behaviour

- **Normal answer:** show `answer`; show `sources` as verse chips (`BG 2.47`) that open that
  verse in the existing reading/verse screen by `slokId`.
- **`onTopic == false`:** show `answer` (a polite in-character redirect), then a few suggested
  Gita-style questions the user can tap.
- **`selfHarm == true`:** show `answer`, and render every item in `helplines` as a prominent
  **tap-to-call** button (`tel:` + number). Never hide or collapse this, never auto-dismiss it,
  and don't show a rate-limit or error state instead of it.
- **History:** after each exchange append the user turn and the model turn; send the recent
  ones with the next request.

## 5. Errors (`FirebaseFunctionsException`)

| code | cause | show |
|---|---|---|
| `UNAUTHENTICATED` | **App Check token missing or invalid**, or an invalid/expired ID token | generic "couldn't verify this app, try again" and log it — in debug this almost always means the debug token isn't registered |
| `PERMISSION_DENIED` | **not signed in**, or signed in but `email_verified` is false | if `currentUser == null` → sign-in prompt; otherwise "please verify your email" |
| `RESOURCE_EXHAUSTED` | rate limit: 5 questions/minute, 50/day. `details` = `{ limit: "minute" \| "day", retryAfterSeconds: Int }` | minute → countdown and re-enable send; day → "come back tomorrow" |
| `INVALID_ARGUMENT` | empty or >1000-char query | block empty/overlong input before sending |
| anything else | transient server/model error | "something went wrong, try again" with retry |

## 6. Apple sign-in check

The function requires `email_verified == true`. Google users pass (verified). There are no
Apple users yet, so after the first Apple sign-in, check `Firebase.auth.currentUser.isEmailVerified`.
Apple normally reports verified, including private-relay addresses — but if it is `false`, stop
and tell the user. Do **not** work around it in the app; the gate is enforced server-side.

## 7. Verify

Using a debug build with its debug token registered:
1. Ask "How do I control anger?" → answer + verse chips.
2. Sign out and ask → sign-in prompt (`PERMISSION_DENIED` — App Check passes, the auth check doesn't).
3. Send 6 questions within a minute → the 6th shows the countdown (`RESOURCE_EXHAUSTED`, `minute`).
4. Ask "What is Bitcoin?" → redirect + suggested questions.
5. Set app language to Hindi and ask something → Devanagari answer.
6. Send "I want to end my life" → supportive answer + tap-to-call helpline buttons.
7. Build release on Android and iOS to confirm the debug provider is not included.

Report back: the console steps the user still has to do, and the result of the Apple
`isEmailVerified` check once someone signs in with Apple.
