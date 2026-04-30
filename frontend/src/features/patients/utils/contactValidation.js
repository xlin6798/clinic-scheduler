export const PHONE_DIGIT_LIMIT = 10;
export const PHONE_INPUT_PLACEHOLDER = "10-digit phone";
export const SSN_DIGIT_LIMIT = 9;
export const PHONE_LABEL_ORDER = ["cell", "home", "work"];
export const PHONE_LABEL_TITLES = {
  cell: "Cell",
  home: "Home",
  work: "Work",
};

export function getDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

export function getCappedDigits(value, maxDigits) {
  return getDigits(value).slice(0, maxDigits);
}

export function getPhoneInputDigits(value) {
  return getCappedDigits(value, PHONE_DIGIT_LIMIT);
}

export function getSsnInputDigits(value) {
  return getCappedDigits(value, SSN_DIGIT_LIMIT);
}

export function formatPhoneInput(value) {
  const digits = getPhoneInputDigits(value);
  if (digits.length <= 2) return digits;
  if (digits.length === 3) return `(${digits})`;
  if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
  return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
}

export function formatPhoneDisplay(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";

  const digits = getDigits(raw);
  const normalized =
    digits.length === 11 && digits.startsWith("1") ? digits.slice(1) : digits;

  if (normalized.length !== PHONE_DIGIT_LIMIT) return raw;
  return `(${normalized.slice(0, 3)})${normalized.slice(3, 6)}-${normalized.slice(6)}`;
}

export function getPhoneLabelTitle(label) {
  const normalized = String(label || "")
    .trim()
    .toLowerCase();
  return PHONE_LABEL_TITLES[normalized] || "Phone";
}

function getPhoneSortRank(phone) {
  const primaryRank = phone.is_primary ? 0 : 1;
  const labelRank = PHONE_LABEL_ORDER.indexOf(phone.label);
  return primaryRank * 10 + (labelRank === -1 ? 9 : labelRank);
}

function normalizePhoneEntry(entry) {
  const number = String(entry?.number || entry?.phone_number || "").trim();
  if (!number) return null;

  const label = String(entry?.label || "")
    .trim()
    .toLowerCase();
  return {
    label,
    labelTitle: getPhoneLabelTitle(label),
    number,
    formattedNumber: formatPhoneDisplay(number),
    is_primary: Boolean(entry?.is_primary),
  };
}

export function getPatientPhoneEntries(patientOrValues) {
  const values = patientOrValues || {};
  const phones = Array.isArray(values.phones)
    ? values.phones.map(normalizePhoneEntry).filter(Boolean)
    : PHONE_LABEL_ORDER.map((label) =>
        normalizePhoneEntry({
          label,
          number: values[`phone_${label}`],
          is_primary: label === "cell",
        })
      ).filter(Boolean);

  if (!phones.length && values.primary_phone_number) {
    phones.push(
      normalizePhoneEntry({
        label: values.primary_phone_label || "primary",
        number: values.primary_phone_number,
        is_primary: true,
      })
    );
  }

  const seen = new Set();
  return phones
    .filter((phone) => {
      const key = getDigits(phone.number) || phone.number;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => getPhoneSortRank(a) - getPhoneSortRank(b));
}

export function formatPhoneEntryDisplay(phone) {
  if (!phone) return "";
  return `${phone.labelTitle} ${phone.formattedNumber}`;
}

export function getPrimaryPatientPhoneDisplay(patientOrValues) {
  const [primaryPhone] = getPatientPhoneEntries(patientOrValues);
  return formatPhoneEntryDisplay(primaryPhone);
}

export function formatSsnInput(value) {
  const digits = getSsnInputDigits(value);
  if (digits.length <= 2) return digits;
  if (digits.length === 3) return `${digits}-`;
  if (digits.length <= 4) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
  if (digits.length === 5) return `${digits.slice(0, 3)}-${digits.slice(3)}-`;
  return `${digits.slice(0, 3)}-${digits.slice(3, 5)}-${digits.slice(5)}`;
}

export function getFormattedBackspaceValue(value, cursorPosition, formatInput) {
  const text = String(value || "");
  if (!cursorPosition || /\d/.test(text[cursorPosition - 1] || "")) return null;

  const digits = getDigits(text);
  const digitIndex = getDigits(text.slice(0, cursorPosition)).length - 1;
  if (digitIndex < 0) return null;

  return formatInput(
    `${digits.slice(0, digitIndex)}${digits.slice(digitIndex + 1)}`
  );
}

export function getFormattedDeleteValue(value, cursorPosition, formatInput) {
  const text = String(value || "");
  if (cursorPosition === null || cursorPosition === undefined) return null;
  if (cursorPosition >= text.length) return null;
  if (/\d/.test(text[cursorPosition] || "")) return null;

  const digits = getDigits(text);
  const nextDigitIndex = getDigits(text.slice(0, cursorPosition)).length;
  const digitIndex =
    nextDigitIndex >= digits.length ? nextDigitIndex - 1 : nextDigitIndex;
  if (digitIndex < 0 || digitIndex >= digits.length) return null;

  return formatInput(
    `${digits.slice(0, digitIndex)}${digits.slice(digitIndex + 1)}`
  );
}

export function handleFormattedInputDeletion(event, formatInput, setValue) {
  if (event.key !== "Backspace" && event.key !== "Delete") return false;

  const input = event.currentTarget;
  if (input.selectionStart !== input.selectionEnd) return false;

  const nextValue =
    event.key === "Backspace"
      ? getFormattedBackspaceValue(
          input.value,
          input.selectionStart,
          formatInput
        )
      : getFormattedDeleteValue(input.value, input.selectionStart, formatInput);

  if (nextValue === null) return false;

  event.preventDefault();
  setValue(nextValue);
  return true;
}

export function validatePhoneNumber(value) {
  const raw = String(value || "").trim();
  if (!raw) return null;

  const digits = getDigits(raw);
  if (digits.length === 10) return null;
  return "Phone number must be 10 digits.";
}

export function validateSsn(value) {
  const digits = getDigits(value);
  if (!digits) return null;
  return digits.length === 9 ? null : "SSN must be exactly 9 digits.";
}
