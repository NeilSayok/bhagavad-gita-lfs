package com.gita.data.db

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.ForeignKey.Companion.CASCADE
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room entities mirroring db/schema.sql.
 * Base image URL is not stored — prepend BuildConfig/const:
 * https://neilsayok.github.io/gita-images/
 */
const val IMAGE_BASE_URL = "https://neilsayok.github.io/gita-images/"

@Entity(tableName = "language")
data class LanguageEntity(
    @PrimaryKey val code: String,
    @ColumnInfo(name = "name_native") val nameNative: String,
    @ColumnInfo(name = "name_en") val nameEn: String,
    @ColumnInfo(name = "is_script_only") val isScriptOnly: Boolean = false,
)

@Entity(tableName = "chapter")
data class ChapterEntity(
    @PrimaryKey @ColumnInfo(name = "chapter_number") val chapterNumber: Int,
    @ColumnInfo(name = "verses_count") val versesCount: Int,
    @ColumnInfo(name = "name_sanskrit") val nameSanskrit: String,
    val translation: String,
    val transliteration: String,
    @ColumnInfo(name = "img_landscape") val imgLandscape: String,
    @ColumnInfo(name = "img_portrait") val imgPortrait: String,
    @ColumnInfo(name = "img_square") val imgSquare: String,
)

@Entity(
    tableName = "chapter_translation",
    primaryKeys = ["chapter_number", "lang_code"],
    foreignKeys = [
        ForeignKey(ChapterEntity::class, ["chapter_number"], ["chapter_number"], onDelete = CASCADE),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("lang_code")],
)
data class ChapterTranslationEntity(
    @ColumnInfo(name = "chapter_number") val chapterNumber: Int,
    @ColumnInfo(name = "lang_code") val langCode: String,
    val meaning: String?,
    val summary: String?,
)

@Entity(
    tableName = "verse",
    foreignKeys = [
        ForeignKey(ChapterEntity::class, ["chapter_number"], ["chapter_number"], onDelete = CASCADE),
    ],
    indices = [Index(value = ["chapter_number", "verse_number"], unique = true)],
)
data class VerseEntity(
    @PrimaryKey @ColumnInfo(name = "verse_id") val verseId: String,
    @ColumnInfo(name = "chapter_number") val chapterNumber: Int,
    @ColumnInfo(name = "verse_number") val verseNumber: Int,
    val transliteration: String,
    @ColumnInfo(name = "img_landscape") val imgLandscape: String,
    @ColumnInfo(name = "img_portrait") val imgPortrait: String,
    @ColumnInfo(name = "img_square") val imgSquare: String,
)

/** Sanskrit verse rendered per script — transliteration, not meaning. */
@Entity(
    tableName = "verse_text",
    primaryKeys = ["verse_id", "lang_code"],
    foreignKeys = [
        ForeignKey(VerseEntity::class, ["verse_id"], ["verse_id"], onDelete = CASCADE),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("lang_code")],
)
data class VerseTextEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    @ColumnInfo(name = "lang_code") val langCode: String,
    val speaker: String?,
    val slok: String?,
)

@Entity(
    tableName = "verse_translation",
    primaryKeys = ["verse_id", "lang_code"],
    foreignKeys = [
        ForeignKey(VerseEntity::class, ["verse_id"], ["verse_id"], onDelete = CASCADE),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("lang_code")],
)
data class VerseTranslationEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    @ColumnInfo(name = "lang_code") val langCode: String,
    @ColumnInfo(name = "life_application") val lifeApplication: String?,
)

@Entity(tableName = "theme", indices = [Index(value = ["slug"], unique = true)])
data class ThemeEntity(
    @PrimaryKey @ColumnInfo(name = "theme_id") val themeId: Int,
    val slug: String,
)

@Entity(
    tableName = "theme_translation",
    primaryKeys = ["theme_id", "lang_code"],
    foreignKeys = [
        ForeignKey(ThemeEntity::class, ["theme_id"], ["theme_id"], onDelete = CASCADE),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("lang_code")],
)
data class ThemeTranslationEntity(
    @ColumnInfo(name = "theme_id") val themeId: Int,
    @ColumnInfo(name = "lang_code") val langCode: String,
    val name: String,
)

@Entity(
    tableName = "verse_theme",
    primaryKeys = ["verse_id", "theme_id"],
    foreignKeys = [
        ForeignKey(VerseEntity::class, ["verse_id"], ["verse_id"], onDelete = CASCADE),
        ForeignKey(ThemeEntity::class, ["theme_id"], ["theme_id"], onDelete = CASCADE),
    ],
    indices = [Index("theme_id")],
)
data class VerseThemeEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    @ColumnInfo(name = "theme_id") val themeId: Int,
    val position: Int,
)

@Entity(
    tableName = "word_meaning",
    primaryKeys = ["verse_id", "position"],
    foreignKeys = [
        ForeignKey(VerseEntity::class, ["verse_id"], ["verse_id"], onDelete = CASCADE),
    ],
)
data class WordMeaningEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    val position: Int,
    val sanskrit: String,
    val transliteration: String,
)

@Entity(
    tableName = "word_meaning_translation",
    primaryKeys = ["verse_id", "position", "lang_code"],
    foreignKeys = [
        ForeignKey(
            WordMeaningEntity::class,
            ["verse_id", "position"],
            ["verse_id", "position"],
            onDelete = CASCADE,
        ),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("lang_code")],
)
data class WordMeaningTranslationEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    val position: Int,
    @ColumnInfo(name = "lang_code") val langCode: String,
    val meaning: String,
)

@Entity(tableName = "commentator")
data class CommentatorEntity(
    @PrimaryKey @ColumnInfo(name = "commentator_key") val commentatorKey: String,
    val author: String,
    @ColumnInfo(name = "display_order") val displayOrder: Int,
)

@Entity(
    tableName = "commentary",
    primaryKeys = ["verse_id", "commentator_key", "lang_code"],
    foreignKeys = [
        ForeignKey(VerseEntity::class, ["verse_id"], ["verse_id"], onDelete = CASCADE),
        ForeignKey(CommentatorEntity::class, ["commentator_key"], ["commentator_key"], onDelete = CASCADE),
        ForeignKey(LanguageEntity::class, ["code"], ["lang_code"], onDelete = CASCADE),
    ],
    indices = [Index("commentator_key"), Index("lang_code")],
)
data class CommentaryEntity(
    @ColumnInfo(name = "verse_id") val verseId: String,
    @ColumnInfo(name = "commentator_key") val commentatorKey: String,
    @ColumnInfo(name = "lang_code") val langCode: String,
    val text: String?,
)
