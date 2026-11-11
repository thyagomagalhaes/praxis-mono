package app.suasflux.modulo.config;

import java.util.Objects;

import javax.sql.DataSource;

import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.autoconfigure.DataSourceProperties;
import org.springframework.boot.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
        basePackages = "app.suasflux.modulo.acolhimento",
        entityManagerFactoryRef = "acolhimentoEntityManagerFactory",
        transactionManagerRef = "acolhimentoTransactionManager"
)
public class AcolhimentoDbConfig {
	
	@Primary
    @Bean
    @ConfigurationProperties("app.datasource.acolhimento")
    public DataSourceProperties acolhimentoDataSourceProperties() {
        return new DataSourceProperties();
    }
	
	@Primary
    @Bean
    public DataSource acolhimentoDataSource(
            @Qualifier("acolhimentoDataSourceProperties") DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
	
	@Primary
    @Bean
    public Flyway acolhimentoFlyway(
            @Qualifier("acolhimentoDataSource") DataSource dataSource) {
        return Flyway.configure()
                .dataSource(dataSource)
                .locations(
                    "classpath:db/setupschema/acolhimento",
                    "classpath:db/migration/acolhimento",
                    "classpath:db/legacydata/acolhimento"
                )
                .baselineOnMigrate(true)  // Útil para DBs existentes
                .load();
    }
	
	@Primary
    @Bean
    @DependsOn("acolhimentoFlyway")  // Garante ordem sem injeção fantasma
    public LocalContainerEntityManagerFactoryBean acolhimentoEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("acolhimentoDataSource") DataSource dataSource) {
        
        return builder
                .dataSource(dataSource)
                .packages("app.suasflux.modulo.acolhimento")
                .persistenceUnit("acolhimento")
                .build();
    }
	
	@Primary
    @Bean
    public PlatformTransactionManager acolhimentoTransactionManager(
            @Qualifier("acolhimentoEntityManagerFactory") 
            LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        
        return new JpaTransactionManager(
            Objects.requireNonNull(entityManagerFactory.getObject(), 
                "EntityManagerFactory não inicializada")
        );
    }
}