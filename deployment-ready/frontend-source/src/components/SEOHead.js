import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import axios from '@/api/axios';

const SEOHead = ({ title, description, image, url, type = 'website', additionalMeta = [] }) => {
  const [seoSettings, setSeoSettings] = useState(null);

  useEffect(() => {
    fetchSEOSettings();
  }, []);

  const fetchSEOSettings = async () => {
    try {
      const response = await axios.get('/admin/seo-settings/active');
      setSeoSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch SEO settings:', error);
    }
  };

  if (!seoSettings) return null;

  const pageTitle = title || seoSettings.site_title;
  const pageDescription = description || seoSettings.site_description;
  const pageImage = image || seoSettings.og_image;
  const pageUrl = url || seoSettings.og_url || window.location.href;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{pageTitle}</title>
      <meta name="description" content={pageDescription} />
      {seoSettings.site_keywords && (
        <meta name="keywords" content={seoSettings.site_keywords} />
      )}
      {seoSettings.author && <meta name="author" content={seoSettings.author} />}
      <meta name="robots" content="index, follow" />
      <link rel="canonical" href={pageUrl} />
      
      {/* Open Graph Tags */}
      <meta property="og:title" content={seoSettings.og_title || pageTitle} />
      <meta property="og:description" content={seoSettings.og_description || pageDescription} />
      {pageImage && <meta property="og:image" content={pageImage} />}
      <meta property="og:url" content={pageUrl} />
      <meta property="og:type" content={type} />
      {seoSettings.og_site_name && (
        <meta property="og:site_name" content={seoSettings.og_site_name} />
      )}

      {/* Twitter Card Tags */}
      <meta name="twitter:card" content={seoSettings.twitter_card || 'summary_large_image'} />
      {seoSettings.twitter_site && (
        <meta name="twitter:site" content={seoSettings.twitter_site} />
      )}
      {seoSettings.twitter_creator && (
        <meta name="twitter:creator" content={seoSettings.twitter_creator} />
      )}
      <meta name="twitter:title" content={seoSettings.twitter_title || pageTitle} />
      <meta name="twitter:description" content={seoSettings.twitter_description || pageDescription} />
      {(seoSettings.twitter_image || pageImage) && (
        <meta name="twitter:image" content={seoSettings.twitter_image || pageImage} />
      )}

      {/* Analytics */}
      {seoSettings.google_site_verification && (
        <meta name="google-site-verification" content={seoSettings.google_site_verification} />
      )}
      {seoSettings.facebook_domain_verification && (
        <meta name="facebook-domain-verification" content={seoSettings.facebook_domain_verification} />
      )}

      {/* Additional Meta Tags */}
      {additionalMeta.map((meta, index) => (
        <meta key={index} {...meta} />
      ))}

      {/* Google Analytics */}
      {seoSettings.google_analytics_id && (
        <>
          <script async src={`https://www.googletagmanager.com/gtag/js?id=${seoSettings.google_analytics_id}`}></script>
          <script>
            {`
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${seoSettings.google_analytics_id}');
            `}
          </script>
        </>
      )}

      {/* Google Tag Manager */}
      {seoSettings.google_tag_manager_id && (
        <script>
          {`
            (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','${seoSettings.google_tag_manager_id}');
          `}
        </script>
      )}

      {/* Structured Data - Organization */}
      {seoSettings.organization_name && (
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Organization",
            name: seoSettings.organization_name,
            description: seoSettings.organization_description,
            url: seoSettings.organization_url || window.location.origin,
            logo: seoSettings.organization_logo,
            email: seoSettings.organization_email,
            telephone: seoSettings.organization_phone,
            sameAs: seoSettings.organization_social_profiles || []
          })}
        </script>
      )}

      {/* Structured Data - WebSite */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebSite",
          name: seoSettings.site_title,
          description: seoSettings.site_description,
          url: window.location.origin
        })}
      </script>
    </Helmet>
  );
};

export default SEOHead;
