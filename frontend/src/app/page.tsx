import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[90vh] flex items-center justify-center bg-gradient-to-r from-primary-red to-secondary-red">
        <div className="absolute inset-0 bg-black opacity-40"></div>
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            Got Blood?
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto">
            Join us in revolutionizing blood donation and management across hospitals.
            Every drop counts, every life matters.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/donate" className="btn-secondary">
              Donate Blood
            </Link>
            <Link href="/register" className="btn-primary">
              Register Hospital
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="heading-1 text-center mb-16">Why Choose Got Blood?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="text-4xl mb-4">🗺️</div>
              <h3 className="heading-3">Interactive Map</h3>
              <p className="text-gray-600">
                Real-time visualization of blood availability across hospitals and donation centers.
              </p>
            </div>
            <div className="card text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="heading-3">Smart Analytics</h3>
              <p className="text-gray-600">
                Data-driven insights for optimal blood routing and inventory management.
              </p>
            </div>
            <div className="card text-center">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="heading-3">Easy Coordination</h3>
              <p className="text-gray-600">
                Seamless communication between hospitals and blood banks.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="py-20 bg-off-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="heading-1 text-center mb-16">Our Impact</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-red mb-2">500+</div>
              <div className="text-gray-600">Hospitals Connected</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-red mb-2">10K+</div>
              <div className="text-gray-600">Lives Saved</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-red mb-2">50K+</div>
              <div className="text-gray-600">Donors Registered</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-red mb-2">24/7</div>
              <div className="text-gray-600">Support Available</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-red text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-8">
            Ready to Make a Difference?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join our network of hospitals and donors to create a more efficient blood management system.
          </p>
          <Link href="/register" className="btn-secondary">
            Get Started Today
          </Link>
        </div>
      </section>
    </div>
  );
}
