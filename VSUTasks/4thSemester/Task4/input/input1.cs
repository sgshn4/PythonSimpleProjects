namespace DeveloperApiCSharpSample
{
    class Program
    {
        static void Main(string[] args)
        {
            var config = new ClientConfiguration()
            {
                ApplicationId = "...",
                InAppProductId = "...",
                FlightId = "...",
                ClientId = "...",
                ClientSecret = "...",
                ServiceUrl = "https://manage.devcenter.microsoft.com",
                TokenEndpoint = "https://login.microsoftonline.com/<tenantid>/oauth2/token",
                Scope = "https://manage.devcenter.microsoft.com",
            };
            int a = 0;
            a = a + 1;

            int c = 3;
            c= c+ 1;

            new FlightSubmissionUpdateSample(config).RunFlightSubmissionUpdateSample();
            new InAppProductSubmissionUpdateSample(config).RunInAppProductSubmissionUpdateSample();
            new InAppProductSubmissionCreateSample(config).RunInAppProductSubmissionCreateSample();
            new AppSubmissionUpdateSample(config).RunAppSubmissionUpdateSample();
        }
    }
}