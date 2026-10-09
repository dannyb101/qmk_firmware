// Copyright 2023 QMK
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

enum unicode_names {
    SMILE,
    SNEK,
    THUMBS_UP,
    JOY,
    SALUTE,
    SLIGHT_SMILE,
    ROCKET,
    THANKS,
    ONE_HUNDRED,
    APPROVED,
    HIGH_FIVE,
    CELEBRATE,
    HEART,
    FIRE,
    GRIMACE
};

enum tap_dance_names {
    TD_L1_CW_TOGG
};

static bool td_l1_cw_togg_layer2_on;

enum custom_keycodes {
    HEART_EMOJI = SAFE_RANGE
};

const uint32_t PROGMEM unicode_map[] = {
    [SLIGHT_SMILE] = 0x1F642,  // 🙂 Slightly Smiling Face
    [ROCKET] = 0x1F680,        // 🚀 Rocket
    [THANKS] = 0x1F64F,        // 🙏 Folded Hands
    [ONE_HUNDRED] = 0x1F4AF,   // 💯 Hundred Points
    [APPROVED] = 0x2705,       // ✅ Check Mark Button

    [CELEBRATE] = 0x1F389,     // 🎉 Party Popper
    [HEART] = 0x2764,          // ❤️ Heart
    [FIRE] = 0x1F525,          // 🔥 Fire
    [JOY] = 0x1F602,           // 😂 Face With Tears of Joy

    [SALUTE] = 0x1FAE1,        // 🫡 Saluting Face
    [HIGH_FIVE] = 0x1F64C,     // 🙌 Raising Hands
    [GRIMACE] = 0x1F62C,        // 😬 Grimacing Face

    [SMILE] = 0x1F600,         // 😀 Grinning Face
    [SNEK] = 0x1F40D,          // 🐍 Snake
    [THUMBS_UP] = 0x1F44D,     // 👍 Thumbs Up
};

// Single tap: enable Caps Word. Double tap: toggle layer 1. Hold: momentarily
// enable layer 2; the reset callback turns it off when the key is released.
void td_l1_cw_togg_finished(tap_dance_state_t *state, void *user_data) {
    if (state->count == 1) {
        if (state->pressed) {
            layer_on(2);
            td_l1_cw_togg_layer2_on = true;
        } else {
            caps_word_on();
        }
    } else if (state->count == 2) {
        layer_invert(1);
    }
}

void td_l1_cw_togg_reset(tap_dance_state_t *state, void *user_data) {
    if (td_l1_cw_togg_layer2_on) {
        layer_off(2);
        td_l1_cw_togg_layer2_on = false;
    }
}

tap_dance_action_t tap_dance_actions[] = {
    [TD_L1_CW_TOGG] = ACTION_TAP_DANCE_FN_ADVANCED(NULL, td_l1_cw_togg_finished, td_l1_cw_togg_reset),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (keycode == HEART_EMOJI) {
        if (record->event.pressed) {
            send_unicode_string("❤️");
        }
        return false;
    }
    return true;
}

bool caps_word_press_user(uint16_t keycode) {
    switch (keycode) {
        case KC_A ... KC_Z:
            add_weak_mods(MOD_BIT(KC_LSFT));
            return true;

        case KC_1 ... KC_0:
        case KC_BSPC:
        case KC_DEL:
        case KC_MINS:
            return true;

        default:
            return false;
    }
}

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    [0] = LAYOUT(
        KC_ESC,             KC_1,   KC_2,   KC_3,       KC_4,       KC_5,                                       KC_6,                               KC_7,   KC_8,       KC_9,   KC_0,       KC_MINS,
        KC_TAB,             KC_Q,   KC_W,   KC_E,       KC_R,       KC_T,                                       KC_Y,                               KC_U,   KC_I,       KC_O,   KC_P,       KC_BSPC,
        TD(TD_L1_CW_TOGG),  KC_A,   KC_S,   KC_D,       KC_F,       KC_G,                                       KC_H,                               KC_J,   KC_K,       KC_L,   KC_SCLN,    KC_QUOT,
        KC_LSFT,            KC_Z,   KC_X,   KC_C,       KC_V,       KC_B,                                       KC_N,                               KC_M,   KC_COMM,    KC_DOT, KC_SLSH,    KC_ENT,
                                            KC_LALT,    KC_LGUI,    MT(MOD_LCTL, KC_SPC),                       MT(MOD_LCTL | MOD_LSFT, KC_SPC),    MO(1),  MO(2)
    ),
    [1] = LAYOUT(
        KC_GRV,     KC_F1,              KC_F2,          KC_NUHS,    KC_F4,              KC_F5,                  KC_MPLY,    KC_MPRV,        KC_MNXT,    KC_VOLD,        KC_VOLU,    KC_PLUS,
        _______,    UM(SLIGHT_SMILE),   UM(ROCKET),     UM(THANKS), UM(ONE_HUNDRED),    UM(APPROVED),           LCMD(KC_V), LOPT(KC_LEFT),  KC_UP,      LOPT(KC_RGHT),  KC_LBRC,    _______,
        _______,    UM(CELEBRATE),      HEART_EMOJI,    UM(FIRE),   UM(JOY),            XXXXXXX,                LCMD(KC_C), KC_LEFT,        KC_DOWN,    KC_RGHT,        KC_RBRC,    KC_BSLS,
        _______,    UM(SALUTE),         UM(HIGH_FIVE),  _______,    XXXXXXX,            XXXXXXX,                LCMD(KC_Z), LCMD(KC_LEFT),  XXXXXXX,    LCMD(KC_RGHT),  _______,    _______,
                                                        _______,    _______,            _______,                QK_LLCK,    _______,        _______
    ),
    [2] = LAYOUT(
        _______,    _______,    _______,    _______,    _______,    _______,                                    _______,    _______,        LCAG(KC_UP),    _______,        _______,    _______,
        _______,    _______,    _______,    _______,    _______,    _______,                                    _______,    LAG(KC_LEFT),   LAG(KC_ENT),    LAG(KC_RGHT),   _______,    _______,
        _______,    _______,    _______,    _______,    _______,    _______,                                    _______,    LCAG(KC_LEFT),  LCAG(KC_DOWN),  LCAG(KC_RGHT),  _______,    _______,
        _______,    _______,    _______,    _______,    _______,    _______,                                    _______,    _______,        LCTL(KC_UP),  _______,        _______,    _______,
                                            _______,    _______,    _______,                                    QK_LLCK,    _______,        _______
    )
};

