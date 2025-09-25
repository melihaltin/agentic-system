import { notFound } from "next/navigation";
import { getRequestConfig } from "next-intl/server";

// Can be imported from a shared config
export const locales = ["en"] as const;
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ locale }) => {
  console.log(`DEBUG - i18n.ts received locale: ${locale}`);

  // Use default locale if none provided
  const selectedLocale = locale || "tr";
  console.log(`DEBUG - Selected locale for processing: ${selectedLocale}`);

  // Validate that the locale parameter is valid
  if (!locales.includes(selectedLocale as any)) {
    console.error(
      `Invalid locale: ${selectedLocale}. Available locales: ${locales.join(
        ", "
      )}`
    );
    // Use default locale as fallback instead of notFound
    const fallbackLocale = "tr";
    try {
      console.log(`DEBUG - Using fallback locale: ${fallbackLocale}`);
      const messages = (await import(`./messages/${fallbackLocale}.json`))
        .default;
      return {
        messages,
        locale: fallbackLocale,
      };
    } catch (error) {
      console.error(`Error loading fallback messages:`, error);
      return {
        messages: {},
        locale: fallbackLocale,
      };
    }
  }

  try {
    console.log(
      `DEBUG - Attempting to load messages for locale: ${selectedLocale}`
    );
    const messages = (await import(`./messages/${selectedLocale}.json`))
      .default;
    console.log(
      `DEBUG - Successfully loaded messages for locale: ${selectedLocale}`
    );
    return {
      messages,
      locale: selectedLocale,
    };
  } catch (error) {
    console.error(
      `Error loading messages for locale ${selectedLocale}:`,
      error
    );
    // Return empty messages as fallback
    return {
      messages: {},
      locale: selectedLocale,
    };
  }
});
