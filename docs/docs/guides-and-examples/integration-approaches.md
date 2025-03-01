---
title: Integration Approaches
---

## Client Side SDK Flag endpoints are public

The API endpoints that our SDKs make calls to are all public. Your Environment API key should also be considered public.
Think if it in the same way you would a Google Analytics key.

### Segment and Targeting rules are not leaked to the client

If flags are evaluated within the client-side SDKs (Web Browser, Mobile App), the entire set of rules for targeting
users based on Segments etc need to be sent to the client. Given these endpoints are public by default, we think this is
a leak of potentially sensitive information. We think the best place for your flags to be evaluated is on our server or
your server. Not on the client.

### You can get your flags with a single HTTP GET

You don't need to run a set of complicated rule evaluations to get your flags. Just hit our endpoint and you get your
flags. You won't receive any information on Segments or rollout rules, and this is by design. If you want to run your
own HTTP client within your application it's just an HTTP GET and you're good.

### Build Time Flag Retrieval

:::tip

We have a [Flagsmith CLI](https://github.com/Flagsmith/flagsmith-cli) which can be helpful here!

:::

A more advanced technique is to grab the Flag defaults from the Flagsmith API at build time and include them on your
application build. The steps for this might look something like this:

1. Push your code to your git repository.
2. An automated build pipeline is triggered.
3. One stage of the pipeline is to grab the current default flag states from the `/flags` endpoint and store the JSON
   response within your application build.
4. Upon startup of your application, read the JSON file is embedded within your application first to get sane default
   flags and config.
5. Asynchronously call the Flagsmith API to get the most recent Flag and Config values.

## Caching Flags Locally

This approach depends on whether your application has an ability to persist data to the host OS during runtime. Locally
caching flags within your application environment ensures that you can subsequently start your application without
having to block for a call to the Flagsmith API. A common workflow would then be:

1. Build your application with sane defaults.
2. Start your app, using the sane defaults, and asynchronously call the Flagsmith API to retrieve up-to-date Flags.
3. Once the up-to-date Flags are retrieved, store them locally.
4. On subsequent app launches, check local storage to see if any flags are available. If they are, load them
   immediately.
5. Asynchronously call the Flagsmith API to retrieve the up-to-date Flags.

The official [Javascript Client](/clients/javascript/) offers optional caching built in to the SDK.

## Caching Flags on a Server

:::tip

Note that you can also [evaluate flags locally](../clients/overview.md) in our Server Side SDKs.

:::

When running the Flagsmith SDK within a Server environment, it is difficult for the SDK to ascertain what sort of
caching infrastructure is available to it. For this reason, caching flags in a Server Environment needs to be integrated
by hand. However, it's pretty simple!

1. When a server starts up, get the Flags from the Flagsmith API. They will now be in memory within the server runtime.
2. If you have caching infrastructure available (for example, memcache, redis etc), you can then store the flags for
   that environment within your caching infrastructure.
3. You can set up a [Web Hook](/advanced-use/system-administration.md#web-hooks) within Flagsmith that sends flag change
   events to your server infrastructure.
4. Write an API endpoint within your infrastructure that receives flag change events and stores them in your local
   cache.
5. You can now rely on your local cache to get up to date flags.
